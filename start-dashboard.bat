@echo off
chcp 65001 >nul
echo ========================================
echo  🎯 芯片产品作战看板
echo  启动中...
echo ========================================
echo.

echo 📍 工作目录：%CD%
echo.

echo 🚀 启动 Streamlit 服务...
echo.
echo 💡 浏览器会自动打开 http://localhost:8501
echo.
echo ⚠️  如需关闭，按 Ctrl+C
echo.
echo ========================================
echo.

C:\Users\59605\AppData\Local\Python\pythoncore-3.14-64\python.exe -m streamlit run dashboard\chip_dashboard.py --server.port 8501 --server.headless true

pause
