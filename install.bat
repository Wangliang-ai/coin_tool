@echo off
chcp 65001 > nul
echo =====================================
echo 社交媒体爬虫工具 - 安装脚本
echo =====================================
echo.

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未检测到Python环境
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

echo [2/3] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖包安装失败
    pause
    exit /b 1
)
echo.

echo [3/3] 创建快捷启动脚本...
echo @echo off > start.bat
echo python run.py >> start.bat
echo.

echo =====================================
echo 安装完成！
echo =====================================
echo.
echo 使用方法:
echo   - 双击 start.bat 启动程序
echo   - 或运行: python run.py
echo.
pause
