"""
数据库模型
"""
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from config import DATABASE_PATH

class Database:
    """数据库管理类"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """初始化数据库"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    avatar TEXT,
                    description TEXT,
                    followers INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, user_id)
                )
            ''')
            
            # 帖子表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    post_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    content TEXT,
                    images TEXT,
                    videos TEXT,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    post_url TEXT,
                    published_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, post_id)
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_posts_platform_user 
                ON posts(platform, user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_posts_published_at 
                ON posts(published_at DESC)
            ''')
    
    def add_user(self, platform, user_id, username, avatar=None, 
                 description=None, followers=0):
        """添加或更新用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (platform, user_id, username, avatar, 
                                   description, followers, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(platform, user_id) DO UPDATE SET
                    username = excluded.username,
                    avatar = excluded.avatar,
                    description = excluded.description,
                    followers = excluded.followers,
                    updated_at = excluded.updated_at
            ''', (platform, user_id, username, avatar, description, 
                  followers, datetime.now()))
            return cursor.lastrowid
    
    def add_post(self, platform, post_id, user_id, username, content=None,
                 images=None, videos=None, likes=0, comments=0, shares=0,
                 post_url=None, published_at=None):
        """添加或更新帖子"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO posts (platform, post_id, user_id, username, content,
                                   images, videos, likes, comments, shares,
                                   post_url, published_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(platform, post_id) DO UPDATE SET
                    content = excluded.content,
                    images = excluded.images,
                    videos = excluded.videos,
                    likes = excluded.likes,
                    comments = excluded.comments,
                    shares = excluded.shares,
                    updated_at = excluded.updated_at
            ''', (platform, post_id, user_id, username, content, images, videos,
                  likes, comments, shares, post_url, published_at, datetime.now()))
            return cursor.lastrowid
    
    def get_posts(self, platform=None, user_id=None, limit=100, offset=0):
        """获取帖子列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM posts WHERE 1=1'
            params = []
            
            if platform:
                query += ' AND platform = ?'
                params.append(platform)
            
            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)
            
            query += ' ORDER BY published_at DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_users(self, platform=None):
        """获取用户列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if platform:
                cursor.execute('SELECT * FROM users WHERE platform = ? ORDER BY updated_at DESC', 
                              (platform,))
            else:
                cursor.execute('SELECT * FROM users ORDER BY updated_at DESC')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_post_count(self, platform=None, user_id=None):
        """获取帖子数量"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = 'SELECT COUNT(*) as count FROM posts WHERE 1=1'
            params = []
            
            if platform:
                query += ' AND platform = ?'
                params.append(platform)
            
            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)
            
            cursor.execute(query, params)
            return cursor.fetchone()['count']
    
    def delete_user(self, platform, user_id):
        """删除用户及其帖子"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM posts WHERE platform = ? AND user_id = ?', 
                          (platform, user_id))
            cursor.execute('DELETE FROM users WHERE platform = ? AND user_id = ?', 
                          (platform, user_id))

# 全局数据库实例
db = Database()
