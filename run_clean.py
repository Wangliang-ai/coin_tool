"""
清洁运行脚本 - 过滤macOS系统警告
"""
import sys
import os

# macOS特定设置
if sys.platform == 'darwin':
    # 设置环境变量
    os.environ['QT_MAC_WANTS_LAYER'] = '1'
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # 过滤stderr中的macOS系统警告
    import io
    
    class FilteredStderr:
        """过滤特定警告信息的stderr包装器"""
        def __init__(self, original_stderr):
            self.original_stderr = original_stderr
            self.filters = [
                'error messaging the mach port',
                'TSM AdjustCapsLockLEDForKeyTransitionHandling',
                '_ISSetPhysicalKeyboardCapsLockLED',
            ]
        
        def write(self, text):
            # 检查是否包含要过滤的内容
            if not any(f in text for f in self.filters):
                self.original_stderr.write(text)
        
        def flush(self):
            self.original_stderr.flush()
    
    # 替换stderr
    sys.stderr = FilteredStderr(sys.stderr)

# 导入主程序
from main import main

if __name__ == '__main__':
    main()
