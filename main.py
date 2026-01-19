"""
社交媒体爬虫工具 - 主入口
支持微博和抖音账号帖子爬取
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# 在macOS上禁用某些系统警告
if sys.platform == 'darwin':
    os.environ['QT_MAC_WANTS_LAYER'] = '1'
    # 重定向stderr以过滤macOS系统警告
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)

from gui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    """主程序入口"""
    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # macOS特定设置
    if sys.platform == 'darwin':
        QApplication.setAttribute(Qt.AA_DontShowIconsInMenus)
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("社交媒体爬虫工具")
    app.setOrganizationName("CoinTool")
    
    # 设置日志
    setup_logger()
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
