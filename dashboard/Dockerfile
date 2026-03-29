FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用文件
COPY *.py .
COPY kongson_logo.jpg .
COPY data/ ./data/
COPY reports/ ./reports/

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "chip_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
