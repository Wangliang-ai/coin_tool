"""
微博爬虫
使用微博移动端API进行爬取
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime
import json
import re
from .base import BaseCrawler

class WeiboCrawler(BaseCrawler):
    """微博爬虫"""
    
    def __init__(self):
        super().__init__('weibo')
        self.base_url = 'https://m.weibo.cn'
        self.api_url = 'https://m.weibo.cn/api'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Referer': 'https://m.weibo.cn/',
            'Accept': 'application/json',
        })
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        try:
            # 如果是用户名，先转换为UID
            if not user_id.isdigit():
                uid = self._get_uid_by_name(user_id)
                if not uid:
                    self.logger.error(f"未找到用户: {user_id}")
                    return None
                user_id = uid
            
            url = f'{self.api_url}/container/getIndex'
            params = {
                'type': 'uid',
                'value': user_id,
            }
            
            response = self.session.get(url, params=params, timeout=10)
            self.logger.info(f"获取用户信息: {response.json()}")
            self.logger.info(f"获取状态码为: {response.status_code}")
            
            data = response.json()
            self.logger.info(f"获取数据为: {data}")
            
            user_info = data['data']['userInfo']
            return {
                'user_id': str(user_info['id']),
                'username': user_info['screen_name'],
                'avatar': user_info.get('profile_image_url', ''),
                'description': user_info.get('description', ''),
                'followers': user_info.get('followers_count', 0),
            }
            
        except Exception as e:
            self.logger.error(f"获取用户信息异常: {e}")
            return None
    
    def get_user_posts(self, user_id: str, max_count: int = 50) -> List[Dict]:
        """获取用户帖子"""
        try:
            # 如果是用户名，先转换为UID
            if not user_id.isdigit():
                uid = self._get_uid_by_name(user_id)
                if not uid:
                    self.logger.error(f"未找到用户: {user_id}")
                    return []
                user_id = uid
            
            # 获取containerid
            container_id = self._get_container_id(user_id)
            if not container_id:
                self.logger.error(f"获取containerid失败")
                return []
            
            posts = []
            page = 1
            
            while len(posts) < max_count:
                url = f'{self.api_url}/container/getIndex'
                params = {
                    'type': 'uid',
                    'value': user_id,
                    'containerid': container_id,
                    'page': page,
                }
                
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code != 200:
                    break
                
                data = response.json()
                if data.get('ok') != 1:
                    break
                
                cards = data['data'].get('cards', [])
                if not cards:
                    break
                
                for card in cards:
                    if card.get('card_type') != 9:  # 9是微博卡片
                        continue
                    
                    mblog = card.get('mblog')
                    if not mblog:
                        continue
                    
                    post = self._parse_post(mblog)
                    if post:
                        posts.append(post)
                    
                    if len(posts) >= max_count:
                        break
                
                page += 1
                self.sleep()
            
            return posts[:max_count]
            
        except Exception as e:
            self.logger.error(f"获取用户帖子异常: {e}")
            return []
    
    def _get_uid_by_name(self, username: str) -> Optional[str]:
        """通过用户名获取UID"""
        try:
            url = f'{self.api_url}/container/getIndex'
            params = {
                'queryVal': username,
                'containerid': '100103type=3&q=' + username,
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            cards = data.get('data', {}).get('cards', [])
            
            for card in cards:
                if card.get('card_type') == 11:  # 用户卡片
                    card_group = card.get('card_group', [])
                    if card_group:
                        user = card_group[0].get('user')
                        if user and user.get('screen_name') == username:
                            return str(user.get('id'))
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取UID异常: {e}")
            return None
    
    def _get_container_id(self, user_id: str) -> Optional[str]:
        """获取containerid"""
        try:
            url = f'{self.api_url}/container/getIndex'
            params = {
                'type': 'uid',
                'value': user_id,
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            tabs = data.get('data', {}).get('tabsInfo', {}).get('tabs', [])
            
            for tab in tabs:
                if tab.get('tab_type') == 'weibo':
                    return tab.get('containerid')
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取containerid异常: {e}")
            return None
    
    def _parse_post(self, mblog: Dict) -> Optional[Dict]:
        """解析帖子"""
        try:
            # 提取文本内容
            text = mblog.get('text', '')
            # 移除HTML标签
            text = re.sub(r'<[^>]+>', '', text)
            
            # 提取图片
            images = []
            pics = mblog.get('pics', [])
            for pic in pics:
                images.append(pic.get('large', {}).get('url', ''))
            
            # 提取视频
            videos = []
            page_info = mblog.get('page_info')
            if page_info and page_info.get('type') == 'video':
                media_info = page_info.get('media_info', {})
                video_url = media_info.get('stream_url_hd') or media_info.get('stream_url')
                if video_url:
                    videos.append(video_url)
            
            # 发布时间
            created_at = mblog.get('created_at', '')
            published_at = self._parse_time(created_at)
            
            return {
                'post_id': str(mblog.get('id', '')),
                'content': text,
                'images': json.dumps(images) if images else None,
                'videos': json.dumps(videos) if videos else None,
                'likes': mblog.get('attitudes_count', 0),
                'comments': mblog.get('comments_count', 0),
                'shares': mblog.get('reposts_count', 0),
                'post_url': f'https://m.weibo.cn/detail/{mblog.get("id")}',
                'published_at': published_at,
            }
            
        except Exception as e:
            self.logger.error(f"解析帖子异常: {e}")
            return None
    
    def _parse_time(self, time_str: str) -> datetime:
        """解析时间"""
        try:
            # 处理相对时间
            if '刚刚' in time_str:
                return datetime.now()
            elif '分钟前' in time_str:
                minutes = int(re.search(r'(\d+)', time_str).group(1))
                return datetime.now() - timedelta(minutes=minutes)
            elif '小时前' in time_str:
                hours = int(re.search(r'(\d+)', time_str).group(1))
                return datetime.now() - timedelta(hours=hours)
            elif '今天' in time_str:
                time_part = re.search(r'(\d{2}:\d{2})', time_str).group(1)
                return datetime.strptime(f'{datetime.now().date()} {time_part}', '%Y-%m-%d %H:%M')
            elif '昨天' in time_str:
                time_part = re.search(r'(\d{2}:\d{2})', time_str).group(1)
                yesterday = datetime.now().date() - timedelta(days=1)
                return datetime.strptime(f'{yesterday} {time_part}', '%Y-%m-%d %H:%M')
            else:
                # 尝试解析完整日期
                return datetime.strptime(time_str, '%a %b %d %H:%M:%S %z %Y')
        except:
            return datetime.now()

from datetime import timedelta
