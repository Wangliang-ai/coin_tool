"""
打包脚本
使用 PyInstaller 打包为 Windows 可执行文件
"""
import os
import sys
import shutil
import PyInstaller.__main__

def build():
    """构建可执行文件"""
    
    # 清理旧的构建文件
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # PyInstaller 参数
    args = [
        'main.py',                          # 入口文件
        '--name=社交媒体爬虫工具',           # 应用名称
        '--windowed',                       # 不显示控制台窗口(Windows)
        '--onefile',                        # 打包成单个文件
        '--clean',                          # 清理临时文件
        '--noconfirm',                      # 不确认覆盖
        
        # 添加数据文件
        '--add-data=config;config',         # 配置目录
        
        # 隐藏导入
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=requests',
        '--hidden-import=sqlite3',
        
        # 排除不需要的模块
        '--exclude-module=pytest',
        '--exclude-module=unittest',
        '--exclude-module=tkinter',
        
        # 图标(如果有的话)
        # '--icon=icon.ico',
    ]
    
    # 在 Windows 上使用 --windowed
    # 在 macOS 上使用 --windowed 会创建 .app 包
    if sys.platform == 'darwin':
        args.remove('--windowed')
    
    print("开始打包...")
    PyInstaller.__main__.run(args)
    print("打包完成! 可执行文件在 dist 目录中")

if __name__ == '__main__':
    build()
