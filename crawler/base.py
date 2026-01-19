"""
爬虫基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
from utils.logger import get_logger

class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.logger = get_logger(f'crawler.{platform}')
        self.session = None
        self.proxy = None
    
    @abstractmethod
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息字典 {user_id, username, avatar, description, followers}
        """
        pass
    
    @abstractmethod
    def get_user_posts(self, user_id: str, max_count: int = 50) -> List[Dict]:
        """
        获取用户帖子列表
        
        Args:
            user_id: 用户ID
            max_count: 最大获取数量
            
        Returns:
            帖子列表，每个帖子包含 {post_id, content, images, videos, likes, 
            comments, shares, post_url, published_at}
        """
        pass
    
    def set_proxy(self, proxy: Dict):
        """设置代理"""
        self.proxy = proxy
    
    def sleep(self, seconds: float = 1.0):
        """随机延迟，避免被封"""
        import random
        delay = seconds + random.uniform(0, 1)
        time.sleep(delay)
    
    def close(self):
        """关闭爬虫，释放资源"""
        if self.session:
            self.session.close()
