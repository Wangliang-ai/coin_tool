#!/bin/bash

echo "====================================="
echo "社交媒体爬虫工具 - 安装脚本"
echo "====================================="
echo

echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未检测到Python环境"
    echo "请先安装Python 3.8或更高版本"
    exit 1
fi
python3 --version
echo

echo "[2/3] 安装依赖包..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误: 依赖包安装失败"
    exit 1
fi
echo

echo "[3/3] 创建快捷启动脚本..."
cat > start.sh << 'EOF'
#!/bin/bash
python3 run.py
EOF
chmod +x start.sh
echo

echo "====================================="
echo "安装完成！"
echo "====================================="
echo
echo "使用方法:"
echo "  - 运行: ./start.sh"
echo "  - 或运行: python3 run.py"
echo
