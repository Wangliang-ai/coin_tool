#!/bin/bash
# 启动脚本 (Mac/Linux)

echo "正在启动社交媒体爬虫工具..."

# macOS优先使用清洁版本（过滤系统警告）
if [[ "$OSTYPE" == "darwin"* ]] && [ -f "run_clean.py" ]; then
    echo "使用清洁模式（已过滤系统警告）"
    python3 run_clean.py
else
    python3 run.py
fi
