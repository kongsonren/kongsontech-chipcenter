@echo off
chcp 65001 > nul
echo ========================================
echo    微信公众号发布助手 - 依赖安装
echo ========================================
echo.

echo [1/2] 安装 Playwright...
echo.

REM 使用系统 Python 安装
python -m pip install playwright

echo.
echo [2/2] 安装浏览器...
echo.

REM 安装 Chromium 浏览器
python -m playwright install chromium

echo.
echo ========================================
echo    安装完成！
echo ========================================
echo.
echo 下一步:
echo 1. 双击运行 start-dashboard.bat 启动看板
echo 2. 选择"📱 公众号发布"页面
echo 3. 选择产品并生成文案
echo 4. 点击"启动发布助手"测试
echo.
pause
