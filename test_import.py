"""
测试导入脚本 - 验证所有模块是否正确
"""
import sys

def test_imports():
    """测试所有模块导入"""
    print("开始测试模块导入...")
    print("=" * 50)
    
    tests = []
    
    # 测试配置模块
    try:
        import config
        print("✓ config 模块导入成功")
        tests.append(True)
    except Exception as e:
        print(f"✗ config 模块导入失败: {e}")
        tests.append(False)
    
    # 测试数据库模块
    try:
        from models import Database, db
        print("✓ models.database 模块导入成功")
        tests.append(True)
    except Exception as e:
        print(f"✗ models.database 模块导入失败: {e}")
        tests.append(False)
    
    # 测试爬虫模块
    try:
        from crawler import BaseCrawler, WeiboCrawler, DouyinCrawler, DouyinMockCrawler
        print("✓ crawler 模块导入成功")
        tests.append(True)
    except Exception as e:
        print(f"✗ crawler 模块导入失败: {e}")
        tests.append(False)
    
    # 测试爬虫管理器
    try:
        from crawler.manager import CrawlerManager
        print("✓ crawler.manager 模块导入成功")
        tests.append(True)
    except Exception as e:
        print(f"✗ crawler.manager 模块导入失败: {e}")
        tests.append(False)
    
    # 测试工具模块
    try:
        from utils import setup_logger, get_logger
        print("✓ utils 模块导入成功")
        tests.append(True)
    except Exception as e:
        print(f"✗ utils 模块导入失败: {e}")
        tests.append(False)
    
    # 测试GUI模块(可能因为没有安装PyQt5而失败)
    try:
        from gui import MainWindow
        print("✓ gui 模块导入成功")
        tests.append(True)
    except ImportError as e:
        print(f"⚠ gui 模块导入失败(可能需要安装PyQt5): {e}")
        tests.append(False)
    except Exception as e:
        print(f"✗ gui 模块导入失败: {e}")
        tests.append(False)
    
    print("=" * 50)
    success_count = sum(tests)
    total_count = len(tests)
    print(f"测试结果: {success_count}/{total_count} 个模块导入成功")
    
    if success_count == total_count:
        print("✓ 所有模块导入测试通过!")
        return 0
    elif success_count >= total_count - 1:
        print("⚠ 大部分模块导入成功，可能需要安装PyQt5")
        return 0
    else:
        print("✗ 存在模块导入错误，请检查代码")
        return 1

if __name__ == '__main__':
    sys.exit(test_imports())
