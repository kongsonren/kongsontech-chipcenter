#!/bin/bash
# 芯片作战指挥中心 - 云服务器部署脚本
# 适用于 Ubuntu 20.04/22.04

set -e

echo "======================================"
echo " 芯片产品作战指挥中心 - 部署脚本"
echo "======================================"

# 1. 更新系统
echo "[1/8] 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装 Python 3.10+
echo "[2/8] 安装 Python..."
sudo apt install -y python3 python3-pip python3-venv

# 3. 安装系统依赖
echo "[3/8] 安装系统依赖..."
sudo apt install -y nginx supervisor

# 4. 创建应用目录
echo "[4/8] 创建应用目录..."
sudo mkdir -p /opt/chip-dashboard
sudo mkdir -p /var/log/chip-dashboard
sudo mkdir -p /var/www/chip-dashboard

# 5. 创建 Python 虚拟环境
echo "[5/8] 创建 Python 虚拟环境..."
cd /opt/chip-dashboard
sudo python3 -m venv venv
sudo chown -R $USER:$USER /opt/chip-dashboard

# 6. 激活虚拟环境并安装依赖
echo "[6/8] 安装 Python 依赖..."
source /opt/chip-dashboard/venv/bin/activate
pip install --upgrade pip
# 稍后上传 requirements.txt 后再执行
# pip install -r requirements.txt

# 7. 配置 Supervisor (进程守护)
echo "[7/8] 配置 Supervisor..."
sudo tee /etc/supervisor/conf.d/chip-dashboard.conf > /dev/null << EOF
[program:chip-dashboard]
command=/opt/chip-dashboard/venv/bin/streamlit run /opt/chip-dashboard/dashboard/chip_dashboard.py --server.port 8501 --server.address 0.0.0.0
directory=/opt/chip-dashboard
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/chip-dashboard/err.log
stdout_logfile=/var/log/chip-dashboard/out.log
environment=PYTHONUNBUFFERED="1"
EOF

# 8. 配置 Nginx (反向代理)
echo "[8/8] 配置 Nginx..."
sudo tee /etc/nginx/sites-available/chip-dashboard > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # 请替换为您的域名

    # 重定向到 HTTPS (配置 SSL 后启用)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持 (Streamlit 需要)
        proxy_read_timeout 86400;
    }

    # 静态文件缓存
    location /_stcore/static {
        proxy_pass http://localhost:8501;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        add_header Cache-Control "public, max-age=31536000";
    }
}
EOF

# 启用 Nginx 配置
sudo ln -sf /etc/nginx/sites-available/chip-dashboard /etc/nginx/sites-enabled/
sudo nginx -t

# 启动服务
echo ""
echo "正在启动服务..."
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start chip-dashboard

echo ""
echo "======================================"
echo " ✅ 部署完成！"
echo "======================================"
echo ""
echo "下一步操作："
echo "1. 将项目文件上传到 /opt/chip-dashboard/"
echo "2. 运行：source /opt/chip-dashboard/venv/bin/activate"
echo "3. 运行：pip install -r requirements.txt"
echo "4. 修改 /etc/nginx/sites-available/chip-dashboard 中的域名"
echo "5. 配置 SSL 证书 (推荐 Let's Encrypt)"
echo "6. 访问：http://your-domain.com"
echo ""
