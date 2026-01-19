"""
监控模块 - 轮询爬取和关键词过滤
"""
from typing import List, Dict, Set
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from datetime import datetime, timedelta
from models.database import db
from config import config
from utils.logger import get_logger

class MonitorService(QObject):
    """监控服务"""
    
    # 信号
    keyword_matched = pyqtSignal(dict)  # 关键词匹配信号 {post, keywords}
    monitor_status = pyqtSignal(str)  # 监控状态信号
    
    def __init__(self, crawler_manager):
        super().__init__()
        self.crawler_manager = crawler_manager
        self.logger = get_logger('monitor')
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_updates)
        self.is_running = False
        self.last_check_time = {}  # 记录每个用户的最后检查时间
        self.seen_posts: Set[str] = set()  # 已经看过的帖子ID
        
    def start(self):
        """启动监控"""
        if self.is_running:
            self.logger.warning("监控已在运行中")
            return
        
        interval = config.get('monitor.interval', 60) * 1000  # 转换为毫秒
        self.timer.start(interval)
        self.is_running = True
        self.logger.info(f"监控已启动，间隔: {interval/1000}秒")
        self.monitor_status.emit("监控运行中...")
        
        # 初始化已见帖子集合
        self._load_existing_posts()
    
    def stop(self):
        """停止监控"""
        if not self.is_running:
            return
        
        self.timer.stop()
        self.is_running = False
        self.logger.info("监控已停止")
        self.monitor_status.emit("监控已停止")
    
    def _load_existing_posts(self):
        """加载现有帖子，避免重复通知"""
        posts = db.get_posts(limit=1000)
        for post in posts:
            post_key = f"{post['platform']}_{post['post_id']}"
            self.seen_posts.add(post_key)
        self.logger.info(f"已加载 {len(self.seen_posts)} 条历史帖子")
    
    def _check_updates(self):
        """检查更新"""
        if not config.get('monitor.enabled', False):
            return
        
        # 获取要监控的用户
        users = self._get_monitor_users()
        if not users:
            self.logger.debug("没有配置监控用户")
            return
        
        self.logger.info(f"开始检查更新，共 {len(users)} 个用户")
        
        for platform, user_id in users:
            self._check_user_updates(platform, user_id)
    
    def _get_monitor_users(self) -> List[tuple]:
        """获取要监控的用户列表"""
        users = []
        
        # 微博用户
        if config.get('weibo.enabled', False):
            weibo_users = config.get('weibo.users', [])
            for user in weibo_users:
                if isinstance(user, dict):
                    users.append(('weibo', user.get('user_id')))
                else:
                    users.append(('weibo', user))
        
        # 抖音用户
        if config.get('douyin.enabled', False):
            douyin_users = config.get('douyin.users', [])
            for user in douyin_users:
                if isinstance(user, dict):
                    users.append(('douyin', user.get('user_id')))
                else:
                    users.append(('douyin', user))
        
        # 如果配置中没有，从数据库获取
        if not users:
            db_users = db.get_users()
            for user in db_users:
                users.append((user['platform'], user['user_id']))
        
        return users
    
    def _check_user_updates(self, platform: str, user_id: str):
        """检查单个用户的更新"""
        try:
            # 检查是否正在爬取
            if self.crawler_manager.is_running(platform, user_id):
                self.logger.debug(f"跳过 {platform}/{user_id}，正在爬取中")
                return
            
            # 创建爬虫线程
            thread = self.crawler_manager.start_crawler(platform, user_id, max_posts=20)
            
            # 连接信号，检测新帖子
            thread.new_post.connect(self._on_new_post)
            thread.finished.connect(lambda p, c: self._on_check_finished(platform, user_id, c))
            
            self.logger.debug(f"检查 {platform}/{user_id} 的更新")
            
        except Exception as e:
            self.logger.error(f"检查用户更新失败 {platform}/{user_id}: {e}")
    
    def _on_new_post(self, post_data: dict):
        """处理新帖子"""
        platform = post_data.get('platform', '')
        post_id = post_data.get('post_id', '')
        post_key = f"{platform}_{post_id}"
        
        # 检查是否是新帖子
        if post_key in self.seen_posts:
            return
        
        self.seen_posts.add(post_key)
        
        # 检查关键词匹配
        matched_keywords = self._check_keywords(post_data)
        if matched_keywords:
            self.logger.info(f"关键词匹配: {post_data.get('username')} - {matched_keywords}")
            
            # 发送匹配信号
            self.keyword_matched.emit({
                'post': post_data,
                'keywords': matched_keywords
            })
    
    def _check_keywords(self, post_data: dict) -> List[str]:
        """检查关键词匹配"""
        keywords = config.get('monitor.keywords', [])
        if not keywords:
            return []
        
        content = post_data.get('content', '').lower()
        if not content:
            return []
        
        match_mode = config.get('monitor.match_mode', 'any')
        matched = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            if keyword_lower and keyword_lower in content:
                matched.append(keyword)
        
        # 根据匹配模式返回结果
        if match_mode == 'all':
            # 全部匹配模式：所有关键词都要匹配
            return matched if len(matched) == len(keywords) else []
        else:
            # 任意匹配模式：匹配任意一个即可
            return matched
    
    def _on_check_finished(self, platform: str, user_id: str, count: int):
        """检查完成"""
        self.last_check_time[f"{platform}_{user_id}"] = datetime.now()
        if count > 0:
            self.logger.debug(f"检查完成 {platform}/{user_id}: 发现 {count} 条帖子")
    
    def set_interval(self, seconds: int):
        """设置监控间隔"""
        if self.is_running:
            self.timer.setInterval(seconds * 1000)
            self.logger.info(f"监控间隔已更新为 {seconds} 秒")
    
    def add_keyword(self, keyword: str):
        """添加关键词"""
        keywords = config.get('monitor.keywords', [])
        if keyword and keyword not in keywords:
            keywords.append(keyword)
            config.set('monitor.keywords', keywords)
            config.save_config()
            self.logger.info(f"已添加关键词: {keyword}")
    
    def remove_keyword(self, keyword: str):
        """删除关键词"""
        keywords = config.get('monitor.keywords', [])
        if keyword in keywords:
            keywords.remove(keyword)
            config.set('monitor.keywords', keywords)
            config.save_config()
            self.logger.info(f"已删除关键词: {keyword}")
    
    def get_keywords(self) -> List[str]:
        """获取关键词列表"""
        return config.get('monitor.keywords', [])
    
    def clear_seen_posts(self):
        """清除已见帖子记录"""
        self.seen_posts.clear()
        self.logger.info("已清除历史帖子记录")
