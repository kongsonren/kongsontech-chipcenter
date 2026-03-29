@echo off
chcp 65001 > nul
echo ========================================
echo    微信公众号自动发布助手
echo    KR 的自动化工作流 - 2026
echo ========================================
echo.

REM 检查 Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 启动浏览器...
echo.

REM 运行发布脚本（交互模式）
python scripts\wechat_publisher.py --demo

echo.
echo ========================================
echo    发布完成！
echo ========================================
pause
