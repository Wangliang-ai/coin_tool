"""
配置文件
"""
import os
import json
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 数据目录
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# 日志目录
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# 配置文件目录
CONFIG_DIR = BASE_DIR / 'config'
CONFIG_DIR.mkdir(exist_ok=True)

# 数据库文件
DATABASE_PATH = DATA_DIR / 'crawler.db'

# 用户配置文件
USER_CONFIG_PATH = CONFIG_DIR / 'user_config.json'

# 默认配置
DEFAULT_CONFIG = {
    'weibo': {
        'enabled': True,
        'users': [],
        'interval': 300,  # 爬取间隔(秒)
        'max_posts': 50,  # 每次最多爬取帖子数
    },
    'douyin': {
        'enabled': True,
        'users': [],
        'interval': 300,
        'max_posts': 50,
    },
    'proxy': {
        'enabled': False,
        'http': '',
        'https': '',
    },
    'notification': {
        'enabled': True,
        'sound': True,
    },
    'monitor': {
        'enabled': False,  # 是否启用监控
        'interval': 60,  # 监控间隔(秒)
        'keywords': [],  # 关键词列表
        'match_mode': 'any',  # any(任意匹配) 或 all(全部匹配)
        'notification': True,  # 是否弹窗通知
    }
}

class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        if USER_CONFIG_PATH.exists():
            try:
                with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置
                return self._merge_config(DEFAULT_CONFIG.copy(), config)
            except Exception as e:
                print(f"加载配置失败: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """保存配置"""
        try:
            with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def _merge_config(self, default, custom):
        """合并配置"""
        for key, value in custom.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    default[key] = self._merge_config(default[key], value)
                else:
                    default[key] = value
        return default
    
    def get(self, key, default=None):
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

# 全局配置实例
config = Config()
