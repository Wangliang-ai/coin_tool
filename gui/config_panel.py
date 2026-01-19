"""
配置面板
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QLineEdit, QCheckBox, QSpinBox, QPushButton,
                             QMessageBox)
from PyQt5.QtCore import pyqtSignal
from config import config

class ConfigPanel(QWidget):
    """配置面板"""
    
    # 信号
    config_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 微博配置
        weibo_group = QGroupBox("微博配置")
        weibo_layout = QVBoxLayout(weibo_group)
        
        # 启用
        self.weibo_enabled = QCheckBox("启用微博爬取")
        weibo_layout.addWidget(self.weibo_enabled)
        
        # 爬取间隔
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("爬取间隔(秒):"))
        self.weibo_interval = QSpinBox()
        self.weibo_interval.setRange(60, 3600)
        self.weibo_interval.setValue(300)
        interval_layout.addWidget(self.weibo_interval)
        interval_layout.addStretch()
        weibo_layout.addLayout(interval_layout)
        
        # 最大帖子数
        max_posts_layout = QHBoxLayout()
        max_posts_layout.addWidget(QLabel("每次最多爬取帖子数:"))
        self.weibo_max_posts = QSpinBox()
        self.weibo_max_posts.setRange(10, 200)
        self.weibo_max_posts.setValue(50)
        max_posts_layout.addWidget(self.weibo_max_posts)
        max_posts_layout.addStretch()
        weibo_layout.addLayout(max_posts_layout)
        
        layout.addWidget(weibo_group)
        
        # 抖音配置
        douyin_group = QGroupBox("抖音配置")
        douyin_layout = QVBoxLayout(douyin_group)
        
        # 启用
        self.douyin_enabled = QCheckBox("启用抖音爬取")
        douyin_layout.addWidget(self.douyin_enabled)
        
        # 爬取间隔
        dy_interval_layout = QHBoxLayout()
        dy_interval_layout.addWidget(QLabel("爬取间隔(秒):"))
        self.douyin_interval = QSpinBox()
        self.douyin_interval.setRange(60, 3600)
        self.douyin_interval.setValue(300)
        dy_interval_layout.addWidget(self.douyin_interval)
        dy_interval_layout.addStretch()
        douyin_layout.addLayout(dy_interval_layout)
        
        # 最大帖子数
        dy_max_posts_layout = QHBoxLayout()
        dy_max_posts_layout.addWidget(QLabel("每次最多爬取帖子数:"))
        self.douyin_max_posts = QSpinBox()
        self.douyin_max_posts.setRange(10, 200)
        self.douyin_max_posts.setValue(50)
        dy_max_posts_layout.addWidget(self.douyin_max_posts)
        dy_max_posts_layout.addStretch()
        douyin_layout.addLayout(dy_max_posts_layout)
        
        layout.addWidget(douyin_group)
        
        # 代理配置
        proxy_group = QGroupBox("代理配置")
        proxy_layout = QVBoxLayout(proxy_group)
        
        # 启用代理
        self.proxy_enabled = QCheckBox("启用代理")
        proxy_layout.addWidget(self.proxy_enabled)
        
        # HTTP代理
        http_layout = QHBoxLayout()
        http_layout.addWidget(QLabel("HTTP代理:"))
        self.http_proxy = QLineEdit()
        self.http_proxy.setPlaceholderText("http://127.0.0.1:7890")
        http_layout.addWidget(self.http_proxy)
        proxy_layout.addLayout(http_layout)
        
        # HTTPS代理
        https_layout = QHBoxLayout()
        https_layout.addWidget(QLabel("HTTPS代理:"))
        self.https_proxy = QLineEdit()
        self.https_proxy.setPlaceholderText("http://127.0.0.1:7890")
        https_layout.addWidget(self.https_proxy)
        proxy_layout.addLayout(https_layout)
        
        layout.addWidget(proxy_group)
        
        # 通知配置
        notification_group = QGroupBox("通知配置")
        notification_layout = QVBoxLayout(notification_group)
        
        self.notification_enabled = QCheckBox("启用通知")
        notification_layout.addWidget(self.notification_enabled)
        
        self.notification_sound = QCheckBox("启用声音提示")
        notification_layout.addWidget(self.notification_sound)
        
        layout.addWidget(notification_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("💾 保存配置")
        self.save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("🔄 重置")
        self.reset_btn.clicked.connect(self.load_config)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
    
    def load_config(self):
        """加载配置"""
        # 微博
        self.weibo_enabled.setChecked(config.get('weibo.enabled', True))
        self.weibo_interval.setValue(config.get('weibo.interval', 300))
        self.weibo_max_posts.setValue(config.get('weibo.max_posts', 50))
        
        # 抖音
        self.douyin_enabled.setChecked(config.get('douyin.enabled', True))
        self.douyin_interval.setValue(config.get('douyin.interval', 300))
        self.douyin_max_posts.setValue(config.get('douyin.max_posts', 50))
        
        # 代理
        self.proxy_enabled.setChecked(config.get('proxy.enabled', False))
        self.http_proxy.setText(config.get('proxy.http', ''))
        self.https_proxy.setText(config.get('proxy.https', ''))
        
        # 通知
        self.notification_enabled.setChecked(config.get('notification.enabled', True))
        self.notification_sound.setChecked(config.get('notification.sound', True))
    
    def save_config(self):
        """保存配置"""
        # 微博
        config.set('weibo.enabled', self.weibo_enabled.isChecked())
        config.set('weibo.interval', self.weibo_interval.value())
        config.set('weibo.max_posts', self.weibo_max_posts.value())
        
        # 抖音
        config.set('douyin.enabled', self.douyin_enabled.isChecked())
        config.set('douyin.interval', self.douyin_interval.value())
        config.set('douyin.max_posts', self.douyin_max_posts.value())
        
        # 代理
        config.set('proxy.enabled', self.proxy_enabled.isChecked())
        config.set('proxy.http', self.http_proxy.text().strip())
        config.set('proxy.https', self.https_proxy.text().strip())
        
        # 通知
        config.set('notification.enabled', self.notification_enabled.isChecked())
        config.set('notification.sound', self.notification_sound.isChecked())
        
        # 保存到文件
        if config.save_config():
            QMessageBox.information(self, "成功", "配置已保存")
            self.config_saved.emit()
        else:
            QMessageBox.warning(self, "失败", "配置保存失败")
