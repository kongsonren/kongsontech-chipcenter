# 芯片作战指挥中心 - 云服务器部署指南

## 📋 部署前准备

### 1. 云服务器信息
- **云服务商**: 腾讯云/阿里云/华为云
- **操作系统**: Ubuntu 22.04 LTS (推荐)
- **配置要求**: 2 核 CPU / 4GB 内存 / 5Mbps 带宽
- **开放端口**: 80(HTTP), 443(HTTPS), 22(SSH)

### 2. 域名准备
- **域名**: 已备案域名（中国大陆服务器必须）
- **DNS 解析**: 将域名 A 记录指向服务器 IP

---

## 🚀 部署步骤

### 步骤 1：连接服务器

```bash
# 使用 SSH 连接
ssh root@your-server-ip

# 或使用腾讯云/阿里云的网页终端
```

### 步骤 2：运行部署脚本

```bash
# 上传部署脚本到服务器
# 方法 1: 使用 scp
scp deploy.sh root@your-server-ip:/tmp/

# 方法 2: 使用 Git
git clone <your-repo-url> /tmp/chip-automation-workflow

# 在服务器上执行
cd /tmp
chmod +x deploy.sh
./deploy.sh
```

### 步骤 3：上传项目文件

```bash
# 从本地上传整个项目
scp -r C:\projects\chip-automation-workflow\* root@your-server-ip:/opt/chip-dashboard/

# 或在服务器上拉取 Git 仓库
cd /opt/chip-dashboard
git clone <your-repo-url> .
```

### 步骤 4：安装依赖

```bash
cd /opt/chip-dashboard
source venv/bin/activate
pip install -r requirements.txt
```

### 步骤 5：配置域名

编辑 Nginx 配置：
```bash
sudo nano /etc/nginx/sites-available/chip-dashboard
```

修改：
```nginx
server_name your-domain.com;  # 改为您的实际域名
```

### 步骤 6：配置 SSL 证书（推荐）

使用 Let's Encrypt 免费证书：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 步骤 7：启动服务

```bash
# 测试 Nginx 配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 启动 Streamlit
sudo supervisorctl restart chip-dashboard

# 查看状态
sudo supervisorctl status chip-dashboard
```

### 步骤 8：验证访问

```bash
# 本地测试
curl http://localhost:8501

# 通过域名访问
curl http://your-domain.com
```

---

## 👥 团队访问配置

### 创建团队账号（可选）

如果需要多用户登录验证：

1. **创建 `.streamlit/secrets.toml`**:
```toml
[passwords]
"kr@example.com" = "hashed_password_1"
"engineer@example.com" = "hashed_password_2"
"designer@example.com" = "hashed_password_3"

[business]
api_key = "your-api-key"
```

2. **生成哈希密码**:
```python
import streamlit_credentials as cred
print(cred._hash_password("admin123"))
```

---

## 🔧 常用运维命令

```bash
# 查看服务状态
sudo supervisorctl status chip-dashboard

# 重启服务
sudo supervisorctl restart chip-dashboard

# 停止服务
sudo supervisorctl stop chip-dashboard

# 查看日志
tail -f /var/log/chip-dashboard/out.log
tail -f /var/log/chip-dashboard/err.log

# Nginx 相关
sudo systemctl status nginx
sudo systemctl restart nginx
sudo nginx -t

# 查看系统资源
htop  # CPU/内存使用
df -h  # 磁盘空间
```

---

## 📊 性能优化建议

### 1. 数据库优化
- 使用 PostgreSQL 替代 SQLite（生产环境）
- 配置数据库连接池

### 2. 缓存配置
- 使用 Redis 缓存频繁查询
- 配置 Streamlit 缓存

### 3. 静态资源
- 配置 Nginx 缓存
- 使用 CDN 加速

### 4. 监控告警
```bash
# 安装监控工具
sudo apt install prometheus node-exporter grafana

# 或使用云服务商自带监控
# 腾讯云监控 / 阿里云云监控
```

---

## 🛡️ 安全建议

### 1. 防火墙配置
```bash
# 仅开放必要端口
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. SSH 加固
```bash
# 修改 /etc/ssh/sshd_config
PasswordAuthentication no  # 禁用密码登录
PermitRootLogin no         # 禁用 root 登录
```

### 3. 定期备份
```bash
# 创建备份脚本
0 2 * * * tar -czf /backup/chip-dashboard-$(date +\%Y\%m\%d).tar.gz /opt/chip-dashboard
```

---

## 📞 故障排查

### 问题 1: 无法访问网站
```bash
# 检查服务状态
sudo supervisorctl status chip-dashboard
sudo systemctl status nginx

# 检查端口监听
netstat -tlnp | grep 8501
netstat -tlnp | grep 80

# 检查防火墙
sudo ufw status
```

### 问题 2: Streamlit 无法启动
```bash
# 查看日志
tail -f /var/log/chip-dashboard/out.log

# 手动测试
cd /opt/chip-dashboard
source venv/bin/activate
streamlit run dashboard/chip_dashboard.py --server.port 8501
```

### 问题 3: 域名无法解析
```bash
# 检查 DNS
ping your-domain.com
nslookup your-domain.com

# 检查 Nginx 配置
cat /etc/nginx/sites-enabled/chip-dashboard
```

---

## 💰 成本预估

| 项目 | 费用 | 周期 |
|------|------|------|
| 云服务器 (2 核 4G) | ¥150-200 | 月 |
| 域名 | ¥60 | 年 |
| SSL 证书 | ¥0 (Let's Encrypt) | 永久免费 |
| 带宽 (5Mbps) | 包含在服务器 | 月 |
| **合计** | **约 ¥2000/年** | |

---

## 📝 部署检查清单

- [ ] 云服务器已购买
- [ ] 域名已备案并解析
- [ ] SSH 可连接服务器
- [ ] 部署脚本已上传并执行
- [ ] 项目文件已上传
- [ ] Python 依赖已安装
- [ ] Nginx 配置已修改（域名）
- [ ] SSL 证书已配置
- [ ] 服务已启动
- [ ] 通过域名可访问
- [ ] 团队账号已创建（可选）
- [ ] 备份策略已配置

---

## 🎯 下一步

部署完成后：
1. 测试所有功能模块
2. 导入实际业务数据
3. 培训团队成员使用
4. 配置监控告警
5. 建立运维文档

---

**部署完成后，您的团队将可以通过 `https://your-domain.com` 访问作战指挥中心！**
