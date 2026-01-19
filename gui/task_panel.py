"""
任务管理面板
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QListWidget, QListWidgetItem, QPushButton, QLabel,
                             QComboBox, QLineEdit, QSpinBox, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from crawler.manager import CrawlerManager
from models.database import db
from config import config
import requests
import json

class TaskPanel(QWidget):
    """任务管理面板"""
    
    # 信号
    crawler_started = pyqtSignal(str, str)  # platform, user_id
    new_post = pyqtSignal(dict)  # post_data
    crawler_finished = pyqtSignal(str, int)  # platform, count
    crawler_error = pyqtSignal(str, str)  # platform, error
    
    def __init__(self, crawler_manager: CrawlerManager):
        super().__init__()
        self.crawler_manager = crawler_manager
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QHBoxLayout(self)
        
        # 左侧：任务列表
        left_layout = QVBoxLayout()
        
        task_group = QGroupBox("爬取任务")
        task_layout = QVBoxLayout(task_group)
        
        # 平台选择
        platform_layout = QHBoxLayout()
        platform_layout.addWidget(QLabel("平台:"))
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["weibo", "douyin"])
        platform_layout.addWidget(self.platform_combo)
        task_layout.addLayout(platform_layout)
        
        # 用户搜索
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索用户:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入用户名搜索（微博）")
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("🔍 搜索")
        self.search_btn.clicked.connect(self._search_user)
        search_layout.addWidget(self.search_btn)
        task_layout.addLayout(search_layout)
        
        # 搜索结果下拉列表
        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel("搜索结果:"))
        self.search_result_combo = QComboBox()
        self.search_result_combo.setPlaceholderText("先搜索用户")
        self.search_result_combo.currentIndexChanged.connect(self._on_user_selected)
        result_layout.addWidget(self.search_result_combo)
        task_layout.addLayout(result_layout)
        
        # 用户ID（自动填充或手动输入）
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("用户ID:"))
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("从搜索结果选择或手动输入")
        user_layout.addWidget(self.user_input)
        task_layout.addLayout(user_layout)
        
        # 帖子数量
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("帖子数量:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 200)
        self.count_spin.setValue(50)
        count_layout.addWidget(self.count_spin)
        task_layout.addLayout(count_layout)
        
        # 开始按钮
        self.start_btn = QPushButton("🚀 开始爬取")
        self.start_btn.clicked.connect(self.start_crawl)
        task_layout.addWidget(self.start_btn)
        
        left_layout.addWidget(task_group)
        
        # 用户列表
        user_group = QGroupBox("已配置用户")
        user_layout = QVBoxLayout(user_group)
        
        self.user_list = QListWidget()
        self.user_list.itemDoubleClicked.connect(self.crawl_user_from_list)
        user_layout.addWidget(self.user_list)
        
        # 删除用户按钮
        self.delete_user_btn = QPushButton("删除选中用户")
        self.delete_user_btn.clicked.connect(self.delete_user)
        user_layout.addWidget(self.delete_user_btn)
        
        left_layout.addWidget(user_group)
        
        layout.addLayout(left_layout, 1)
        
        # 右侧：日志输出
        right_layout = QVBoxLayout()
        
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        # 清除日志按钮
        self.clear_log_btn = QPushButton("清除日志")
        self.clear_log_btn.clicked.connect(self.log_text.clear)
        log_layout.addWidget(self.clear_log_btn)
        
        right_layout.addWidget(log_group)
        
        layout.addLayout(right_layout, 2)
        
        # 加载用户列表
        self.load_users()
    
    def load_users(self):
        """加载用户列表"""
        self.user_list.clear()
        users = db.get_users()
        
        for user in users:
            platform = user.get('platform', '')
            username = user.get('username', '')
            user_id = user.get('user_id', '')
            
            item = QListWidgetItem(f"[{platform}] {username} ({user_id})")
            item.setData(Qt.UserRole, user)
            self.user_list.addItem(item)
    
    def start_crawl(self):
        """开始爬取"""
        platform = self.platform_combo.currentText()
        user_id = self.user_input.text().strip()
        max_posts = self.count_spin.value()
        
        if not user_id:
            QMessageBox.warning(self, "警告", "请输入用户ID")
            return
        
        # 启动爬虫
        thread = self.crawler_manager.start_crawler(platform, user_id, max_posts)
        
        # 连接信号
        thread.progress.connect(self.on_progress)
        thread.new_post.connect(self.on_new_post)
        thread.error.connect(self.on_error)
        thread.finished.connect(self.on_finished)
        
        # 发送启动信号
        self.crawler_started.emit(platform, user_id)
        self.log(f"开始爬取 {platform} 用户 {user_id}")
        
        # 禁用按钮
        self.start_btn.setEnabled(False)
    
    def crawl_user_from_list(self, item):
        """从列表爬取用户"""
        user = item.data(Qt.UserRole)
        platform = user.get('platform', '')
        user_id = user.get('user_id', '')
        
        # 设置参数
        self.platform_combo.setCurrentText(platform)
        self.user_input.setText(user_id)
        
        # 开始爬取
        self.start_crawl()
    
    def delete_user(self):
        """删除用户"""
        current_item = self.user_list.currentItem()
        if not current_item:
            return
        
        user = current_item.data(Qt.UserRole)
        platform = user.get('platform', '')
        user_id = user.get('user_id', '')
        username = user.get('username', '')
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除用户 {username} 及其所有帖子吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            db.delete_user(platform, user_id)
            self.load_users()
            self.log(f"已删除用户 {username}")
    
    def on_progress(self, platform: str, message: str):
        """进度更新"""
        self.log(f"[{platform}] {message}")
    
    def on_new_post(self, post_data: dict):
        """新帖子"""
        platform = post_data.get('platform', '')
        username = post_data.get('username', '')
        self.log(f"[{platform}] 获取到 {username} 的新帖子")
        self.new_post.emit(post_data)
    
    def on_error(self, platform: str, error: str):
        """错误"""
        self.log(f"[{platform}] 错误: {error}")
        self.crawler_error.emit(platform, error)
        self.start_btn.setEnabled(True)
    
    def on_finished(self, platform: str, count: int):
        """完成"""
        self.log(f"[{platform}] 完成，获取 {count} 条帖子")
        self.crawler_finished.emit(platform, count)
        self.start_btn.setEnabled(True)
        self.load_users()
    
    def log(self, message: str):
        """记录日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def _search_user(self):
        """搜索微博用户"""
        platform = self.platform_combo.currentText()
        if platform != 'weibo':
            QMessageBox.information(self, "提示", "用户搜索功能目前仅支持微博平台")
            return
        
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "警告", "请输入搜索关键词")
            return
        
        self.search_btn.setEnabled(False)
        self.search_btn.setText("搜索中...")
        self.log(f"正在搜索用户: {keyword}")
        
        try:
            # 调用微博搜索API
            url = 'https://weibo.com/ajax/side/search'
            params = {'q': keyword}
            
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'zh-CN,zh;q=0.9',
                'origin': 'https://s.weibo.com',
                'referer': 'https://s.weibo.com/',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest'
            }
            
            # 如果配置了cookie，使用配置的cookie
            cookies = self._get_weibo_cookies()
            
            response = requests.get(url, params=params, headers=headers, cookies=cookies, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                users = self._parse_search_results(data)
                
                if users:
                    self.search_result_combo.clear()
                    self.search_result_combo.addItem("-- 请选择用户 --", None)
                    
                    for user in users:
                        # 显示格式：用户名 (ID) - 粉丝数 [认证标识]
                        verified_mark = " ✓" if user.get('verified') else ""
                        followers_display = user.get('followers_str', str(user.get('followers_count', 0)))
                        display_text = f"{user['screen_name']}{verified_mark} (@{user['id']}) - {followers_display} 粉丝"
                        self.search_result_combo.addItem(display_text, user)
                    
                    self.log(f"找到 {len(users)} 个用户")
                    QMessageBox.information(self, "搜索成功", f"找到 {len(users)} 个匹配用户，请从下拉列表选择")
                else:
                    self.log("未找到匹配的用户")
                    QMessageBox.information(self, "提示", "未找到匹配的用户，请尝试其他关键词")
            else:
                self.log(f"搜索失败: HTTP {response.status_code}")
                QMessageBox.warning(self, "错误", f"搜索失败: HTTP {response.status_code}")
                
        except Exception as e:
            self.log(f"搜索异常: {e}")
            QMessageBox.warning(self, "错误", f"搜索异常: {e}")
        
        finally:
            self.search_btn.setEnabled(True)
            self.search_btn.setText("🔍 搜索")
    
    def _get_weibo_cookies(self):
        """获取微博cookies（如果配置了的话）"""
        # 这里可以从配置文件读取用户设置的cookie
        # 暂时返回空字典，使用无登录状态
        return {}
    
    def _parse_search_results(self, data):
        """解析搜索结果"""
        try:
            users = []
            
            # 微博搜索API返回的数据结构: data.users 是用户列表
            if 'data' in data and isinstance(data['data'], dict):
                search_data = data['data']
                
                # 检查users字段（主要用户搜索结果）
                if 'users' in search_data and isinstance(search_data['users'], list):
                    for user in search_data['users']:
                        user_info = self._extract_user_info(user)
                        if user_info:
                            users.append(user_info)
                
                # 检查user字段（单个推荐用户）
                if 'user' in search_data and isinstance(search_data['user'], dict):
                    user_info = self._extract_user_info(search_data['user'])
                    if user_info and user_info not in users:
                        users.insert(0, user_info)  # 插入到最前面
            
            return users[:10]  # 最多返回10个结果
            
        except Exception as e:
            self.log(f"解析搜索结果异常: {e}")
            return []
    
    def _extract_user_info(self, user_data):
        """提取用户信息"""
        try:
            if not isinstance(user_data, dict):
                return None
            
            # 微博API返回的字段
            user_id = user_data.get('id') or user_data.get('idstr') or user_data.get('uid')
            screen_name = user_data.get('screen_name') or user_data.get('name')
            
            if user_id and screen_name:
                # 粉丝数量（可能是数字或字符串）
                followers = user_data.get('followers_count', 0)
                followers_str = user_data.get('followers_count_str', '')
                
                return {
                    'id': str(user_id),
                    'screen_name': screen_name,
                    'followers_count': followers,
                    'followers_str': followers_str or str(followers),
                    'description': user_data.get('description', ''),
                    'avatar': user_data.get('avatar_hd') or user_data.get('profile_image_url', ''),
                    'verified': user_data.get('verified', False),
                    'verified_type': user_data.get('verified_type', -1)
                }
            
            return None
            
        except Exception as e:
            self.log(f"提取用户信息异常: {e}")
            return None
    
    def _on_user_selected(self, index):
        """用户选择事件"""
        if index <= 0:
            return
        
        user_data = self.search_result_combo.currentData()
        if user_data:
            # 自动填充用户ID
            self.user_input.setText(user_data['id'])
            self.log(f"已选择用户: {user_data['screen_name']} (ID: {user_data['id']})")
