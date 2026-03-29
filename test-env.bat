@echo off
chcp.com 65001 > nul
echo ========================================
echo 🧪 Python 环境测试
echo ========================================
echo.

REM 使用完整路径运行 Python
set PYTHON_PATH=C:\Users\59605\AppData\Local\Python\pythoncore-3.14-64\python.exe

echo 测试 1: Python 版本...
%PYTHON_PATH% --version
echo.

echo 测试 2: 检查依赖包...
%PYTHON_PATH% -c "import pdfplumber; print('✅ pdfplumber:', pdfplumber.__version__)"
%PYTHON_PATH% -c "import pandas; print('✅ pandas:', pandas.__version__)"
%PYTHON_PATH% -c "import openpyxl; print('✅ openpyxl:', openpyxl.__version__)"
%PYTHON_PATH% -c "import docx; print('✅ python-docx:', docx.__version__)"
%PYTHON_PATH% -c "import matplotlib; print('✅ matplotlib:', matplotlib.__version__)"
%PYTHON_PATH% -c "import plotly; print('✅ plotly:', plotly.__version__)"
echo.

echo ========================================
echo 🎉 环境测试完成！
echo ========================================
pause
