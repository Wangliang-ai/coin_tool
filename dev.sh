#!/bin/bash
# 开发模式快速启动脚本

echo "正在启动开发模式..."

# 检查是否安装了watchdog
if ! python3 -c "import watchdog" 2>/dev/null; then
    echo "首次运行，正在安装依赖..."
    pip3 install watchdog
fi

# 启动开发模式
python3 dev_mode.py
