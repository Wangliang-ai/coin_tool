"""
开发模式运行脚本
使用 python3 run.py 启动程序
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 运行主程序
from main import main

if __name__ == '__main__':
    main()
