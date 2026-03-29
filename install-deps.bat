@echo off
echo ========================================
echo 安装芯片自动化工作流依赖包
echo ========================================
echo.

echo [1/6] 升级 pip...
python -m pip install --upgrade pip
echo.

echo [2/6] 安装 pdfplumber (PDF 解析)...
python -m pip install pdfplumber
echo.

echo [3/6] 安装 pandas (数据处理)...
python -m pip install pandas
echo.

echo [4/6] 安装 openpyxl (Excel 支持)...
python -m pip install openpyxl
echo.

echo [5/6] 安装 python-docx (Word 文档)...
python -m pip install python-docx
echo.

echo [6/6] 安装 matplotlib + plotly (图表可视化)...
python -m pip install matplotlib plotly
echo.

echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 按任意键验证环境...
pause >nul

python --version
pip --version
echo.
echo 所有依赖包已安装成功！
echo.
pause
