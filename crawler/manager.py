"""
爬虫管理器
"""
from typing import Dict, List
from PyQt5.QtCore import QThread, pyqtSignal
from .weibo_crawler import WeiboCrawler
from .douyin_crawler import DouyinMockCrawler
from models.database import db
from utils.logger import get_logger

class CrawlerThread(QThread):
    """爬虫线程"""
    
    # 信号
    progress = pyqtSignal(str, str)  # platform, message
    new_post = pyqtSignal(dict)  # post_data
    error = pyqtSignal(str, str)  # platform, error_message
    finished = pyqtSignal(str, int)  # platform, post_count
    
    def __init__(self, platform: str, user_id: str, max_posts: int = 50):
        super().__init__()
        self.platform = platform
        self.user_id = user_id
        self.max_posts = max_posts
        self.logger = get_logger('crawler.thread')
        self._is_running = True
    
    def run(self):
        """运行爬虫"""
        try:
            # 创建爬虫实例
            if self.platform == 'weibo':
                crawler = WeiboCrawler()
            elif self.platform == 'douyin':
                crawler = DouyinMockCrawler()  # 使用模拟爬虫
            else:
                self.error.emit(self.platform, f"不支持的平台: {self.platform}")
                return
            
            # 获取用户信息
            self.progress.emit(self.platform, f"正在获取用户信息...")
            user_info = crawler.get_user_info(self.user_id)
            
            if not user_info:
                self.error.emit(self.platform, f"获取用户信息失败: {self.user_id}")
                return
            
            # 保存用户信息
            db.add_user(
                platform=self.platform,
                user_id=user_info['user_id'],
                username=user_info['username'],
                avatar=user_info.get('avatar'),
                description=user_info.get('description'),
                followers=user_info.get('followers', 0)
            )
            
            # 获取帖子
            self.progress.emit(self.platform, f"正在获取帖子列表...")
            posts = crawler.get_user_posts(self.user_id, self.max_posts)
            
            if not posts:
                self.progress.emit(self.platform, f"未获取到新帖子")
                self.finished.emit(self.platform, 0)
                return
            
            # 保存帖子
            new_count = 0
            for post in posts:
                if not self._is_running:
                    break
                
                db.add_post(
                    platform=self.platform,
                    post_id=post['post_id'],
                    user_id=user_info['user_id'],
                    username=user_info['username'],
                    content=post.get('content'),
                    images=post.get('images'),
                    videos=post.get('videos'),
                    likes=post.get('likes', 0),
                    comments=post.get('comments', 0),
                    shares=post.get('shares', 0),
                    post_url=post.get('post_url'),
                    published_at=post.get('published_at')
                )
                
                # 发送新帖子信号
                post_data = {
                    'platform': self.platform,
                    'username': user_info['username'],
                    **post
                }
                self.new_post.emit(post_data)
                new_count += 1
            
            self.progress.emit(self.platform, f"完成，获取 {new_count} 条帖子")
            self.finished.emit(self.platform, new_count)
            
            # 关闭爬虫
            crawler.close()
            
        except Exception as e:
            self.logger.error(f"爬虫异常: {e}")
            self.error.emit(self.platform, str(e))
    
    def stop(self):
        """停止爬虫"""
        self._is_running = False


class CrawlerManager:
    """爬虫管理器"""
    
    def __init__(self):
        self.threads: Dict[str, CrawlerThread] = {}
        self.logger = get_logger('crawler.manager')
    
    def start_crawler(self, platform: str, user_id: str, max_posts: int = 50) -> CrawlerThread:
        """启动爬虫"""
        # 如果已有该平台的爬虫在运行，先停止
        key = f"{platform}_{user_id}"
        if key in self.threads and self.threads[key].isRunning():
            self.threads[key].stop()
            self.threads[key].wait()
        
        # 创建新线程
        thread = CrawlerThread(platform, user_id, max_posts)
        self.threads[key] = thread
        thread.start()
        
        return thread
    
    def stop_crawler(self, platform: str, user_id: str):
        """停止爬虫"""
        key = f"{platform}_{user_id}"
        if key in self.threads:
            self.threads[key].stop()
            self.threads[key].wait()
            del self.threads[key]
    
    def stop_all(self):
        """停止所有爬虫"""
        for thread in self.threads.values():
            thread.stop()
        
        for thread in self.threads.values():
            thread.wait()
        
        self.threads.clear()
    
    def is_running(self, platform: str, user_id: str) -> bool:
        """检查爬虫是否在运行"""
        key = f"{platform}_{user_id}"
        return key in self.threads and self.threads[key].isRunning()
