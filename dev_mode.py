"""
开发模式 - 支持文件监控和自动重启
修改任何.py文件后自动重启应用，提高开发效率
"""
import sys
import os
import subprocess
import time
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("=" * 60)
    print("错误: 缺少 watchdog 模块")
    print("=" * 60)
    print("\n请先安装依赖:")
    print("  pip3 install watchdog")
    print("\n或运行:")
    print("  pip3 install -r requirements.txt")
    print("=" * 60)
    sys.exit(1)

class AppReloader(FileSystemEventHandler):
    """应用重载器"""
    
    def __init__(self, script='run.py'):
        self.script = script
        self.process = None
        self.last_restart = 0
        self.debounce_seconds = 1  # 防抖时间，避免频繁重启
        self.restart_count = 0
        self.start_app()
    
    def start_app(self):
        """启动应用"""
        if self.process:
            print("\n[停止] 终止旧进程...")
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                print("[警告] 进程未响应，强制结束...")
                self.process.kill()
        
        self.restart_count += 1
        print(f"\n{'='*60}")
        print(f"[启动] 应用启动 (第 {self.restart_count} 次)")
        print(f"[时间] {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[脚本] {self.script}")
        print(f"{'='*60}\n")
        
        # 启动新进程
        env = os.environ.copy()
        # 设置环境变量以减少macOS系统警告
        env['PYTHONUNBUFFERED'] = '1'
        
        self.process = subprocess.Popen(
            [sys.executable, self.script],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        # 只监控Python文件
        if not event.src_path.endswith('.py'):
            return
        
        # 防抖：避免连续多次修改导致频繁重启
        current_time = time.time()
        if current_time - self.last_restart < self.debounce_seconds:
            return
        
        # 忽略某些文件
        ignored_patterns = [
            '__pycache__',
            '.pyc',
            'test_',
            '.git',
            'venv',
            'ENV',
            'env'
        ]
        
        if any(pattern in event.src_path for pattern in ignored_patterns):
            return
        
        self.last_restart = current_time
        
        # 获取相对路径，显示更友好
        try:
            rel_path = os.path.relpath(event.src_path)
        except:
            rel_path = event.src_path
        
        print(f"\n{'*'*60}")
        print(f"[检测] 文件已修改: {rel_path}")
        print(f"[操作] 准备重启应用...")
        print(f"{'*'*60}")
        
        self.start_app()
    
    def stop(self):
        """停止应用"""
        if self.process:
            print("\n[停止] 正在终止应用进程...")
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
                print("[完成] 应用已停止")
            except subprocess.TimeoutExpired:
                print("[警告] 强制结束进程...")
                self.process.kill()

def print_banner():
    """打印启动横幅"""
    print("\n" + "="*60)
    print("  社交媒体爬虫工具 - 开发模式")
    print("="*60)
    print("\n✨ 功能特性:")
    print("  • 自动监控 Python 文件变化")
    print("  • 文件修改后自动重启应用")
    print("  • 提高开发调试效率")
    print("\n📂 监控目录:", os.getcwd())
    print("\n💡 使用提示:")
    print("  • 修改任何 .py 文件后自动重启")
    print("  • 按 Ctrl+C 停止开发模式")
    print("  • 生产环境请使用: python3 run.py")
    print("\n" + "="*60)
    print("开发模式已启动，等待文件变化...\n")

def main():
    """主函数"""
    print_banner()
    
    # 创建监控器
    # 优先使用清洁版本（过滤系统警告）
    if os.path.exists('run_clean.py'):
        script_to_run = 'run_clean.py'
    else:
        script_to_run = 'run.py'
    
    # 检查脚本是否存在
    if not os.path.exists(script_to_run):
        print(f"❌ 错误: 未找到 {script_to_run}")
        print(f"   请确保在项目根目录运行此脚本")
        sys.exit(1)
    
    print(f"📝 使用脚本: {script_to_run}")
    
    event_handler = AppReloader(script_to_run)
    observer = Observer()
    
    # 监控当前目录及子目录（排除一些目录）
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + "="*60)
        print("收到停止信号 (Ctrl+C)")
        print("="*60)
        print("\n正在清理资源...")
        observer.stop()
        event_handler.stop()
        print("✓ 开发模式已停止")
        print("="*60 + "\n")
    
    observer.join()

if __name__ == '__main__':
    main()
