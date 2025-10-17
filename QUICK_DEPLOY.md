# 🚀 快速部署指南（5分钟上线）

## 一、本地推送到 GitHub

```bash
# 1. 进入项目目录
cd "d:\Program Files\JetBrains\PythonProject\project-root"

# 2. 初始化 Git（如果还没初始化）
git init
git add .
git commit -m "Initial commit"

# 3. 关联 GitHub 仓库（替换成你的仓库地址）
git remote add origin https://github.com/你的用户名/flask-file-converter.git
git branch -M main
git push -u origin main
```

---

## 二、云服务器一键部署

### 第1步：连接服务器

```bash
ssh root@你的服务器IP
```

### 第2步：安装 Docker（选择你的系统）

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl start docker
sudo systemctl enable docker
```

**CentOS:**
```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl start docker
sudo systemctl enable docker
```

### 第3步：安装 Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 第4步：克隆代码

```bash
cd /opt
git clone https://github.com/你的用户名/flask-file-converter.git flask-app
cd flask-app
```

### 第5步：配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置（重要！必须修改密码）
nano .env
```

**必改项**：
```
DB_PASSWORD=你的强密码123
SECRET_KEY=随机生成的密钥abc123xyz
```

生成随机密钥：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

同时修改 `docker-compose.yml` 里的 MySQL 密码（两处）：
```bash
nano docker-compose.yml
# 找到 MYSQL_ROOT_PASSWORD 和 MYSQL_PASSWORD，改成相同的强密码
```

### 第6步：启动服务

```bash
# 添加执行权限
chmod +x deploy.sh

# 一键启动
./deploy.sh start
```

### 第7步：开放防火墙

**Ubuntu/Debian:**
```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

**CentOS:**
```bash
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

### 第8步：访问应用

浏览器打开：`http://你的服务器IP`

默认账户：
- 用户名：`admin`
- 密码：`admin123`

**🔴 重要：登录后立即修改密码！**

---

## 三、常用维护命令

```bash
cd /opt/flask-app

# 查看状态
./deploy.sh status

# 查看日志
./deploy.sh logs

# 重启服务
./deploy.sh restart

# 停止服务
./deploy.sh stop

# 更新代码
git pull origin main
./deploy.sh restart

# 备份数据库
./deploy.sh backup
```

---

## 四、故障排查

### 容器无法启动？

```bash
# 查看详细日志
docker-compose logs

# 重新构建
./deploy.sh build
./deploy.sh start
```

### 端口被占用？

```bash
# 查看占用情况
netstat -tlnp | grep :80

# 停止冲突服务
systemctl stop apache2  # 或 httpd
```

### 数据库连接失败？

检查 `.env` 和 `docker-compose.yml` 中的数据库密码是否一致！

---

## 五、架构说明

部署后会启动4个容器：

1. **MySQL** - 数据库（端口3306）
2. **Redis** - 缓存（端口6379）
3. **Flask** - 应用（端口5000）
4. **Nginx** - 反向代理（端口80/443）

数据持久化：
- MySQL数据：`mysql_data` volume
- Redis数据：`redis_data` volume
- 上传文件：`upload_data` volume
- 日志文件：`./logs` 目录

---

## 六、生产环境优化建议

### 1. 使用域名和 HTTPS

编辑 `nginx/nginx.conf`，配置 SSL 证书。

### 2. 修改默认密码

- 管理员账户密码
- MySQL root 密码
- Redis 密码（如需要）

### 3. 定时备份

```bash
# 添加定时任务
crontab -e

# 每天凌晨2点备份
0 2 * * * cd /opt/flask-app && ./deploy.sh backup
```

### 4. 监控日志

```bash
# 实时查看日志
./deploy.sh logs

# 或
docker-compose logs -f --tail=100
```

---

## 🎉 部署完成！

现在你的 Flask 应用已经在云服务器上运行了！

有问题查看详细文档：[README_DEPLOYMENT.md](./README_DEPLOYMENT.md)
