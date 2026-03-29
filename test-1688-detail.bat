@echo off
chcp.com 65001 >nul
echo ====================================
echo 1688 详情页生成器 - 测试脚本
echo ====================================
echo.

echo 正在测试 1688 详情页生成功能...
echo.

python scripts\1688_product.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================
    echo ✅ 测试完成！请查看 output/1688 目录
    echo ====================================
    echo.
    echo 下一步:
    echo 1. 启动看板：start-dashboard.bat
    echo 2. 选择"公众号发布"页面
    echo 3. 选择产品后选择"1688 详情页"
    echo 4. 点击"一键生成文案"
    echo.
) else (
    echo.
    echo ====================================
    echo ❌ 测试失败，请检查 Python 环境
    echo ====================================
    echo.
    echo 请尝试:
    echo 1. 确保已安装 Python 3.8+
    echo 2. 运行：pip install streamlit pandas plotly
    echo.
)

pause
