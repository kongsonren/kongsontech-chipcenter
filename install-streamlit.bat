@echo off
chcp 65001 >nul
echo ========================================
echo  安装 Streamlit 看板环境
echo ========================================
echo.

C:\Users\59605\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pip install streamlit plotly --quiet

if %errorlevel% equ 0 (
    echo.
    echo ✅ Streamlit 安装成功！
    echo.
    echo 运行看板命令：
    echo   streamlit run dashboard\chip_dashboard.py
    echo.
    pause
) else (
    echo.
    echo ❌ 安装失败，请检查网络连接
    pause
)
