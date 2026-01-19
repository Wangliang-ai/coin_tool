"""
监控管理面板
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLabel, QLineEdit, QListWidget,
                             QSpinBox, QCheckBox, QTextEdit, QMessageBox,
                             QListWidgetItem, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from config import config

class MonitorPanel(QWidget):
    """监控管理面板"""
    
    # 信号
    monitor_started = pyqtSignal()
    monitor_stopped = pyqtSignal()
    keywords_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_config()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 监控控制组
        control_group = QGroupBox("监控控制")
        control_layout = QVBoxLayout(control_group)
        
        # 启用监控
        self.monitor_enabled = QCheckBox("启用自动监控")
        self.monitor_enabled.stateChanged.connect(self._on_monitor_toggle)
        control_layout.addWidget(self.monitor_enabled)
        
        # 监控间隔
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("监控间隔(秒):"))
        self.monitor_interval = QSpinBox()
        self.monitor_interval.setRange(10, 3600)
        self.monitor_interval.setValue(60)
        self.monitor_interval.valueChanged.connect(self._on_interval_changed)
        interval_layout.addWidget(self.monitor_interval)
        interval_layout.addWidget(QLabel("建议设置60秒以上"))
        interval_layout.addStretch()
        control_layout.addLayout(interval_layout)
        
        # 启动/停止按钮
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("🚀 启动监控")
        self.start_btn.clicked.connect(self._start_monitor)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏸ 停止监控")
        self.stop_btn.clicked.connect(self._stop_monitor)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        button_layout.addStretch()
        control_layout.addLayout(button_layout)
        
        # 监控状态
        self.status_label = QLabel("状态: 未启动")
        self.status_label.setStyleSheet("color: gray; font-weight: bold;")
        control_layout.addWidget(self.status_label)
        
        layout.addWidget(control_group)
        
        # 关键词管理组
        keyword_group = QGroupBox("关键词管理")
        keyword_layout = QVBoxLayout(keyword_group)
        
        # 说明
        tip_label = QLabel("💡 只有包含设置关键词的帖子才会弹窗通知")
        tip_label.setStyleSheet("color: #666; font-size: 12px;")
        keyword_layout.addWidget(tip_label)
        
        # 匹配模式
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("匹配模式:"))
        self.match_mode = QComboBox()
        self.match_mode.addItems(["任意匹配", "全部匹配"])
        self.match_mode.currentTextChanged.connect(self._on_match_mode_changed)
        mode_layout.addWidget(self.match_mode)
        mode_layout.addWidget(QLabel("(任意匹配: 命中任一关键词即通知)"))
        mode_layout.addStretch()
        keyword_layout.addLayout(mode_layout)
        
        # 添加关键词
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("添加关键词:"))
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入关键词，如：产品、优惠、活动")
        self.keyword_input.returnPressed.connect(self._add_keyword)
        add_layout.addWidget(self.keyword_input)
        
        self.add_btn = QPushButton("➕ 添加")
        self.add_btn.clicked.connect(self._add_keyword)
        add_layout.addWidget(self.add_btn)
        keyword_layout.addLayout(add_layout)
        
        # 关键词列表
        keyword_layout.addWidget(QLabel("当前关键词列表:"))
        self.keyword_list = QListWidget()
        self.keyword_list.setMaximumHeight(150)
        keyword_layout.addWidget(self.keyword_list)
        
        # 删除按钮
        delete_layout = QHBoxLayout()
        self.delete_btn = QPushButton("🗑️ 删除选中")
        self.delete_btn.clicked.connect(self._delete_keyword)
        delete_layout.addWidget(self.delete_btn)
        
        self.clear_btn = QPushButton("清空全部")
        self.clear_btn.clicked.connect(self._clear_keywords)
        delete_layout.addWidget(self.clear_btn)
        
        delete_layout.addStretch()
        keyword_layout.addLayout(delete_layout)
        
        layout.addWidget(keyword_group)
        
        # 通知设置组
        notification_group = QGroupBox("通知设置")
        notification_layout = QVBoxLayout(notification_group)
        
        self.notification_enabled = QCheckBox("启用弹窗通知")
        notification_layout.addWidget(self.notification_enabled)
        
        self.sound_enabled = QCheckBox("启用声音提示")
        notification_layout.addWidget(self.sound_enabled)
        
        layout.addWidget(notification_group)
        
        # 监控日志
        log_group = QGroupBox("监控日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        clear_log_btn = QPushButton("清除日志")
        clear_log_btn.clicked.connect(self.log_text.clear)
        log_layout.addWidget(clear_log_btn)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
    
    def load_config(self):
        """加载配置"""
        # 监控设置
        self.monitor_enabled.setChecked(config.get('monitor.enabled', False))
        self.monitor_interval.setValue(config.get('monitor.interval', 60))
        
        # 匹配模式
        match_mode = config.get('monitor.match_mode', 'any')
        self.match_mode.setCurrentText("任意匹配" if match_mode == 'any' else "全部匹配")
        
        # 通知设置
        self.notification_enabled.setChecked(config.get('monitor.notification', True))
        self.sound_enabled.setChecked(config.get('notification.sound', True))
        
        # 加载关键词
        self._refresh_keywords()
    
    def _refresh_keywords(self):
        """刷新关键词列表"""
        self.keyword_list.clear()
        keywords = config.get('monitor.keywords', [])
        for keyword in keywords:
            self.keyword_list.addItem(keyword)
    
    def _add_keyword(self):
        """添加关键词"""
        keyword = self.keyword_input.text().strip()
        if not keyword:
            return
        
        keywords = config.get('monitor.keywords', [])
        if keyword in keywords:
            QMessageBox.warning(self, "提示", f"关键词 '{keyword}' 已存在")
            return
        
        keywords.append(keyword)
        config.set('monitor.keywords', keywords)
        config.save_config()
        
        self._refresh_keywords()
        self.keyword_input.clear()
        self.log(f"已添加关键词: {keyword}")
        self.keywords_changed.emit()
    
    def _delete_keyword(self):
        """删除选中的关键词"""
        current_item = self.keyword_list.currentItem()
        if not current_item:
            return
        
        keyword = current_item.text()
        keywords = config.get('monitor.keywords', [])
        if keyword in keywords:
            keywords.remove(keyword)
            config.set('monitor.keywords', keywords)
            config.save_config()
            
            self._refresh_keywords()
            self.log(f"已删除关键词: {keyword}")
            self.keywords_changed.emit()
    
    def _clear_keywords(self):
        """清空所有关键词"""
        reply = QMessageBox.question(
            self, "确认",
            "确定要清空所有关键词吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            config.set('monitor.keywords', [])
            config.save_config()
            self._refresh_keywords()
            self.log("已清空所有关键词")
            self.keywords_changed.emit()
    
    def _on_monitor_toggle(self, state):
        """监控开关切换"""
        enabled = state == Qt.Checked
        config.set('monitor.enabled', enabled)
        config.save_config()
    
    def _on_interval_changed(self, value):
        """间隔改变"""
        config.set('monitor.interval', value)
        config.save_config()
    
    def _on_match_mode_changed(self, text):
        """匹配模式改变"""
        mode = 'any' if text == "任意匹配" else 'all'
        config.set('monitor.match_mode', mode)
        config.save_config()
    
    def _start_monitor(self):
        """启动监控"""
        keywords = config.get('monitor.keywords', [])
        if not keywords:
            QMessageBox.warning(self, "提示", "请先添加关键词！")
            return
        
        config.set('monitor.enabled', True)
        config.save_config()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("状态: 运行中")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        
        self.log("监控已启动")
        self.monitor_started.emit()
    
    def _stop_monitor(self):
        """停止监控"""
        config.set('monitor.enabled', False)
        config.save_config()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("状态: 已停止")
        self.status_label.setStyleSheet("color: gray; font-weight: bold;")
        
        self.log("监控已停止")
        self.monitor_stopped.emit()
    
    def log(self, message: str):
        """记录日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def update_status(self, status: str):
        """更新状态"""
        self.log(status)
