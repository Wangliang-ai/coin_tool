"""
主窗口
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QStatusBar, QMessageBox, QDialog,
                             QLabel, QPushButton, QTextEdit, QDialogButtonBox,
                             QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from .post_list import PostListWidget
from .config_panel import ConfigPanel
from .task_panel import TaskPanel
from .monitor_panel import MonitorPanel
from crawler.manager import CrawlerManager
from crawler.monitor import MonitorService
from models.database import db
from config import config
from utils.logger import get_logger
import json

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger('gui')
        self.crawler_manager = CrawlerManager()
        self.monitor_service = MonitorService(self.crawler_manager)
        self.init_ui()
        self.load_data()
        self.setup_monitor()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("社交媒体爬虫工具 v1.0")
        self.setMinimumSize(1200, 800)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 帖子列表页
        self.post_list = PostListWidget()
        self.tab_widget.addTab(self.post_list, "📝 帖子列表")
        
        # 任务管理页
        self.task_panel = TaskPanel(self.crawler_manager)
        self.tab_widget.addTab(self.task_panel, "⚙️ 任务管理")
        
        # 监控管理页
        self.monitor_panel = MonitorPanel()
        self.tab_widget.addTab(self.monitor_panel, "📡 监控管理")
        
        # 配置页
        self.config_panel = ConfigPanel()
        self.tab_widget.addTab(self.config_panel, "🔧 设置")
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 连接信号
        self.connect_signals()
        
        # 定时刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(5000)  # 5秒刷新一次
    
    def connect_signals(self):
        """连接信号"""
        # 任务面板信号
        self.task_panel.crawler_started.connect(self.on_crawler_started)
        self.task_panel.new_post.connect(self.on_new_post)
        self.task_panel.crawler_finished.connect(self.on_crawler_finished)
        self.task_panel.crawler_error.connect(self.on_crawler_error)
        
        # 配置面板信号
        self.config_panel.config_saved.connect(self.on_config_saved)
        
        # 监控面板信号
        self.monitor_panel.monitor_started.connect(self.on_monitor_started)
        self.monitor_panel.monitor_stopped.connect(self.on_monitor_stopped)
    
    def load_data(self):
        """加载数据"""
        self.post_list.load_posts()
    
    def auto_refresh(self):
        """自动刷新"""
        # 刷新帖子列表
        if self.tab_widget.currentWidget() == self.post_list:
            self.post_list.load_posts()
        
        # 更新状态栏
        post_count = db.get_post_count()
        self.status_bar.showMessage(f"共 {post_count} 条帖子")
    
    def on_crawler_started(self, platform: str, user_id: str):
        """爬虫启动"""
        self.status_bar.showMessage(f"{platform} - 开始爬取用户 {user_id}")
    
    def on_new_post(self, post_data: dict):
        """新帖子"""
        platform = post_data.get('platform', '')
        username = post_data.get('username', '')
        self.status_bar.showMessage(f"📬 {platform} - {username} 发布了新帖子")
        
        # 刷新列表
        self.post_list.load_posts()
    
    def on_crawler_finished(self, platform: str, count: int):
        """爬虫完成"""
        self.status_bar.showMessage(f"✅ {platform} - 完成，获取 {count} 条帖子")
        self.post_list.load_posts()
    
    def on_crawler_error(self, platform: str, error: str):
        """爬虫错误"""
        self.status_bar.showMessage(f"❌ {platform} - 错误: {error}")
        QMessageBox.warning(self, "错误", f"{platform} 爬取失败:\n{error}")
    
    def on_config_saved(self):
        """配置已保存"""
        self.status_bar.showMessage("配置已保存")
    
    def setup_monitor(self):
        """设置监控服务"""
        # 连接监控服务信号
        self.monitor_service.keyword_matched.connect(self.on_keyword_matched)
        self.monitor_service.monitor_status.connect(self.monitor_panel.update_status)
    
    def on_monitor_started(self):
        """监控启动"""
        self.monitor_service.start()
        self.status_bar.showMessage("📡 监控已启动")
        self.logger.info("监控服务已启动")
    
    def on_monitor_stopped(self):
        """监控停止"""
        self.monitor_service.stop()
        self.status_bar.showMessage("监控已停止")
        self.logger.info("监控服务已停止")
    
    def on_keyword_matched(self, data: dict):
        """关键词匹配通知"""
        post = data['post']
        keywords = data['keywords']
        
        # 记录日志
        self.logger.info(f"关键词匹配: {post.get('username')} - {keywords}")
        
        # 显示弹窗通知
        if config.get('monitor.notification', True):
            self.show_keyword_notification(post, keywords)
        
        # 更新状态栏
        keyword_str = ', '.join(keywords)
        self.status_bar.showMessage(f"🔔 发现匹配: {post.get('username')} - 关键词: {keyword_str}")
    
    def show_keyword_notification(self, post: dict, keywords: list):
        """显示关键词匹配通知对话框"""
        dialog = KeywordNotificationDialog(post, keywords, self)
        dialog.exec_()
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止监控
        self.monitor_service.stop()
        
        # 停止所有爬虫
        self.crawler_manager.stop_all()
        
        # 停止定时器
        self.refresh_timer.stop()
        
        event.accept()


class KeywordNotificationDialog(QDialog):
    """关键词匹配通知对话框"""
    
    def __init__(self, post: dict, keywords: list, parent=None):
        super().__init__(parent)
        self.post = post
        self.keywords = keywords
        self.init_ui()
        
        # 播放声音（如果启用）
        if config.get('notification.sound', True):
            self.play_notification_sound()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("🔔 关键词匹配通知")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("📬 发现匹配的新帖子！")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF5722;")
        layout.addWidget(title)
        
        # 关键词提示
        keyword_str = ', '.join(self.keywords)
        keyword_label = QLabel(f"匹配关键词: {keyword_str}")
        keyword_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 14px;")
        layout.addWidget(keyword_label)
        
        # 分割线
        layout.addSpacing(10)
        
        # 用户信息
        user_layout = QHBoxLayout()
        platform = self.post.get('platform', '').upper()
        username = self.post.get('username', '')
        user_layout.addWidget(QLabel(f"<b>用户:</b> {username} [{platform}]"))
        user_layout.addStretch()
        layout.addLayout(user_layout)
        
        # 发布时间
        published_at = self.post.get('published_at', '')
        if published_at:
            layout.addWidget(QLabel(f"<b>发布时间:</b> {published_at}"))
        
        # 内容
        layout.addWidget(QLabel("<b>内容:</b>"))
        content_text = QTextEdit()
        content = self.post.get('content', '')
        
        # 高亮关键词
        highlighted_content = content
        for keyword in self.keywords:
            highlighted_content = highlighted_content.replace(
                keyword, 
                f'<span style="background-color: yellow; color: red; font-weight: bold;">{keyword}</span>'
            )
        
        content_text.setHtml(highlighted_content)
        content_text.setReadOnly(True)
        layout.addWidget(content_text)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        likes = self.post.get('likes', 0)
        comments = self.post.get('comments', 0)
        shares = self.post.get('shares', 0)
        stats_layout.addWidget(QLabel(f"👍 {likes}"))
        stats_layout.addWidget(QLabel(f"💬 {comments}"))
        stats_layout.addWidget(QLabel(f"🔄 {shares}"))
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # 链接
        post_url = self.post.get('post_url', '')
        if post_url:
            url_label = QLabel(f'<a href="{post_url}">🔗 查看原帖</a>')
            url_label.setOpenExternalLinks(True)
            layout.addWidget(url_label)
        
        # 按钮
        button_box = QDialogButtonBox()
        
        view_btn = QPushButton("📝 查看详情")
        view_btn.clicked.connect(self.accept)
        button_box.addButton(view_btn, QDialogButtonBox.AcceptRole)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        button_box.addButton(close_btn, QDialogButtonBox.RejectRole)
        
        layout.addWidget(button_box)
    
    def play_notification_sound(self):
        """播放通知声音"""
        try:
            # 使用系统默认提示音
            from PyQt5.QtMultimedia import QSound
            # 可以使用系统音效或自定义音频文件
            # QSound.play("notification.wav")
        except:
            pass  # 如果没有音频支持，跳过
