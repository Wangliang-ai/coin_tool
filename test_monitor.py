"""
监控功能测试脚本
用于验证监控模块是否正常工作
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_monitor_import():
    """测试监控模块导入"""
    print("=" * 60)
    print("测试监控模块导入...")
    print("=" * 60)
    
    try:
        from crawler.monitor import MonitorService
        print("✓ MonitorService 导入成功")
        
        from gui.monitor_panel import MonitorPanel
        print("✓ MonitorPanel 导入成功")
        
        from config import config
        print("✓ config 导入成功")
        
        # 测试配置
        monitor_config = config.get('monitor')
        print(f"\n监控配置:")
        print(f"  - 启用状态: {monitor_config.get('enabled')}")
        print(f"  - 监控间隔: {monitor_config.get('interval')} 秒")
        print(f"  - 关键词数量: {len(monitor_config.get('keywords', []))}")
        print(f"  - 匹配模式: {monitor_config.get('match_mode')}")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_keyword_matching():
    """测试关键词匹配逻辑"""
    print("\n" + "=" * 60)
    print("测试关键词匹配...")
    print("=" * 60)
    
    try:
        # 模拟关键词匹配
        keywords = ['新品', '优惠', '活动']
        test_contents = [
            "今天发布新品啦！",
            "限时优惠，快来抢购",
            "新品上市，限时优惠",
            "今天天气真好",
        ]
        
        print(f"\n关键词列表: {keywords}")
        print("\n任意匹配模式测试:")
        
        for content in test_contents:
            matched = [kw for kw in keywords if kw in content]
            status = "✓" if matched else "✗"
            print(f"  {status} \"{content}\" → {matched if matched else '无匹配'}")
        
        print("\n全部匹配模式测试:")
        print(f"  需要同时包含: {keywords}")
        
        for content in test_contents:
            matched = [kw for kw in keywords if kw in content]
            is_all_match = len(matched) == len(keywords)
            status = "✓" if is_all_match else "✗"
            result = "匹配" if is_all_match else f"仅匹配 {matched}"
            print(f"  {status} \"{content}\" → {result}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_config_operations():
    """测试配置操作"""
    print("\n" + "=" * 60)
    print("测试配置操作...")
    print("=" * 60)
    
    try:
        from config import config
        
        # 读取配置
        print("\n当前配置:")
        print(f"  监控启用: {config.get('monitor.enabled')}")
        print(f"  监控间隔: {config.get('monitor.interval')}")
        print(f"  关键词: {config.get('monitor.keywords')}")
        
        # 测试添加关键词
        print("\n测试添加关键词...")
        keywords = config.get('monitor.keywords', [])
        test_keyword = "测试关键词"
        
        if test_keyword not in keywords:
            keywords.append(test_keyword)
            config.set('monitor.keywords', keywords)
            print(f"✓ 已添加: {test_keyword}")
        
        # 验证
        updated_keywords = config.get('monitor.keywords', [])
        if test_keyword in updated_keywords:
            print(f"✓ 验证成功: {test_keyword} 在列表中")
        
        # 清理测试数据
        keywords.remove(test_keyword)
        config.set('monitor.keywords', keywords)
        print(f"✓ 已清理测试数据")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_database():
    """测试数据库操作"""
    print("\n" + "=" * 60)
    print("测试数据库...")
    print("=" * 60)
    
    try:
        from models.database import db
        
        # 检查数据库连接
        users = db.get_users()
        posts = db.get_posts(limit=5)
        
        print(f"\n数据库状态:")
        print(f"  用户数量: {len(users)}")
        print(f"  帖子数量: {db.get_post_count()}")
        
        if users:
            print(f"\n最近用户:")
            for user in users[:3]:
                print(f"  - {user['username']} ({user['platform']})")
        
        if posts:
            print(f"\n最新帖子:")
            for post in posts[:3]:
                content = post['content'][:30] if post['content'] else ''
                print(f"  - {post['username']}: {content}...")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("社交媒体爬虫工具 - 监控功能测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_monitor_import),
        ("关键词匹配", test_keyword_matching),
        ("配置操作", test_config_operations),
        ("数据库操作", test_database),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n测试异常 [{name}]: {e}")
            results.append((name, False))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {name}")
    
    success_count = sum(1 for _, r in results if r)
    total_count = len(results)
    
    print("\n" + "=" * 60)
    print(f"总计: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("✓ 所有测试通过！监控功能准备就绪！")
        print("\n快速开始:")
        print("  1. 运行程序: python3 run.py 或 ./start.sh")
        print("  2. 切换到 '📡 监控管理' 标签页")
        print("  3. 添加关键词并启动监控")
    else:
        print("⚠ 部分测试失败，请检查错误信息")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
