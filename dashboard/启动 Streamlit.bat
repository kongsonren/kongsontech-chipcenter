@echo off
chcp 65001 >nul
echo ========================================
echo   冠辰科技作战指挥中心 - Streamlit 启动
echo ========================================
echo.
echo 正在启动 Streamlit 服务...
echo.
echo 浏览器会自动打开：http://localhost:8501
echo.
echo 按 Ctrl+C 可停止服务
echo ========================================
echo.
cd /d "%~dp0"
streamlit run chip_dashboard.py --server.port 8501
