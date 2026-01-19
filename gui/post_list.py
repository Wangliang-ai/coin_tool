"""
帖子列表组件
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QComboBox, QLineEdit, QPushButton,
                             QLabel, QHeaderView, QTextEdit, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from models.database import db
import json

class PostListWidget(QWidget):
    """帖子列表组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 筛选栏
        filter_layout = QHBoxLayout()
        
        # 平台筛选
        filter_layout.addWidget(QLabel("平台:"))
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["全部", "weibo", "douyin"])
        self.platform_combo.currentTextChanged.connect(self.load_posts)
        filter_layout.addWidget(self.platform_combo)
        
        # 搜索
        filter_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索内容...")
        self.search_input.returnPressed.connect(self.load_posts)
        filter_layout.addWidget(self.search_input)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self.load_posts)
        filter_layout.addWidget(self.refresh_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # 帖子表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "平台", "用户", "内容", "点赞", "评论", "分享", "发布时间"
        ])
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        # 设置表格属性
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.show_post_detail)
        
        layout.addWidget(self.table)
        
        # 统计信息
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)
    
    def load_posts(self):
        """加载帖子"""
        # 获取筛选条件
        platform = self.platform_combo.currentText()
        if platform == "全部":
            platform = None
        
        # 获取数据
        posts = db.get_posts(platform=platform, limit=1000)
        
        # 搜索过滤
        search_text = self.search_input.text().strip().lower()
        if search_text:
            posts = [p for p in posts if search_text in (p.get('content') or '').lower()]
        
        # 更新表格
        self.table.setRowCount(len(posts))
        
        for i, post in enumerate(posts):
            # 平台
            platform_item = QTableWidgetItem(post.get('platform', ''))
            platform_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, platform_item)
            
            # 用户
            user_item = QTableWidgetItem(post.get('username', ''))
            self.table.setItem(i, 1, user_item)
            
            # 内容（截取前50字符）
            content = post.get('content', '')
            if len(content) > 50:
                content = content[:50] + '...'
            content_item = QTableWidgetItem(content)
            self.table.setItem(i, 2, content_item)
            
            # 点赞
            likes_item = QTableWidgetItem(str(post.get('likes', 0)))
            likes_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, likes_item)
            
            # 评论
            comments_item = QTableWidgetItem(str(post.get('comments', 0)))
            comments_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, comments_item)
            
            # 分享
            shares_item = QTableWidgetItem(str(post.get('shares', 0)))
            shares_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 5, shares_item)
            
            # 发布时间
            published_at = post.get('published_at', '')
            if published_at:
                time_str = published_at.split('.')[0]  # 去掉毫秒
            else:
                time_str = ''
            time_item = QTableWidgetItem(time_str)
            self.table.setItem(i, 6, time_item)
            
            # 存储完整数据
            self.table.item(i, 0).setData(Qt.UserRole, post)
        
        # 更新统计
        self.stats_label.setText(f"共 {len(posts)} 条帖子")
    
    def show_post_detail(self, index):
        """显示帖子详情"""
        row = index.row()
        post = self.table.item(row, 0).data(Qt.UserRole)
        
        dialog = PostDetailDialog(post, self)
        dialog.exec_()


class PostDetailDialog(QDialog):
    """帖子详情对话框"""
    
    def __init__(self, post, parent=None):
        super().__init__(parent)
        self.post = post
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("帖子详情")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 用户信息
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel(f"<b>{self.post.get('username', '')}</b>"))
        user_layout.addWidget(QLabel(f"[{self.post.get('platform', '')}]"))
        user_layout.addStretch()
        layout.addLayout(user_layout)
        
        # 内容
        layout.addWidget(QLabel("<b>内容:</b>"))
        content_text = QTextEdit()
        content_text.setPlainText(self.post.get('content', ''))
        content_text.setReadOnly(True)
        layout.addWidget(content_text)
        
        # 图片/视频
        images = self.post.get('images')
        if images:
            try:
                image_list = json.loads(images)
                layout.addWidget(QLabel(f"<b>图片:</b> {len(image_list)} 张"))
            except:
                pass
        
        videos = self.post.get('videos')
        if videos:
            try:
                video_list = json.loads(videos)
                layout.addWidget(QLabel(f"<b>视频:</b> {len(video_list)} 个"))
            except:
                pass
        
        # 统计数据
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(QLabel(f"👍 {self.post.get('likes', 0)}"))
        stats_layout.addWidget(QLabel(f"💬 {self.post.get('comments', 0)}"))
        stats_layout.addWidget(QLabel(f"🔄 {self.post.get('shares', 0)}"))
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # 链接
        post_url = self.post.get('post_url', '')
        if post_url:
            layout.addWidget(QLabel(f"<b>链接:</b> <a href='{post_url}'>{post_url}</a>"))
        
        # 时间
        published_at = self.post.get('published_at', '')
        if published_at:
            layout.addWidget(QLabel(f"<b>发布时间:</b> {published_at}"))
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
