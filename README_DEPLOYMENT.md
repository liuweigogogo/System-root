# Flask 文件转换系统 - Docker 部署完整指南

## 📋 目录

1. [前置准备](#前置准备)
2. [GitHub 代码托管](#github-代码托管)
3. [云服务器配置](#云服务器配置)
4. [Docker 部署](#docker-部署)
5. [常见问题](#常见问题)
6. [维护管理](#维护管理)

---

## 🛠️ 前置准备

### 1. 本地环境要求

- Git 已安装
- 代码已完成测试
- 配置文件已准备

### 2. 云服务器要求

- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **CPU**: 2核心以上
- **内存**: 4GB 以上
- **硬盘**: 20GB 以上
- **网络**: 开放端口 80, 443, 5000 (可选)

---

## 📤 GitHub 代码托管

### 步骤 1: 创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - Repository name: `flask-file-converter`
   - Description: `Flask文件转换系统`
   - 选择 Private 或 Public
4. 点击 "Create repository"

### 步骤 2: 本地初始化 Git（如果尚未初始化）

```bash
# 进入项目目录
cd "d:\Program Files\JetBrains\PythonProject\project-root"

# 初始化 Git
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: Flask file converter project"
```

### 步骤 3: 关联远程仓库并推送

```bash
# 关联远程仓库（替换成你的仓库地址）
git remote add origin https://github.com/你的用户名/flask-file-converter.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤 4: 验证推送成功

访问你的 GitHub 仓库页面，确认代码已上传。

---

## ☁️ 云服务器配置

### 步骤 1: 连接到云服务器

```bash
# 使用 SSH 连接（替换成你的服务器 IP）
ssh root@your_server_ip

# 或使用密钥连接
ssh -i /path/to/your/key.pem root@your_server_ip
```

### 步骤 2: 更新系统

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS
sudo yum update -y
```

### 步骤 3: 安装 Docker

#### Ubuntu/Debian:

```bash
# 安装必要的包
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### CentOS:

```bash
# 安装必要的包
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 步骤 4: 安装 Docker Compose

```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 步骤 5: 安装 Git

```bash
# Ubuntu/Debian
sudo apt install -y git

# CentOS
sudo yum install -y git
```

---

## 🐳 Docker 部署

### 步骤 1: 克隆代码到服务器

```bash
# 创建项目目录
sudo mkdir -p /opt/flask-app
cd /opt/flask-app

# 克隆代码（替换成你的仓库地址）
sudo git clone https://github.com/你的用户名/flask-file-converter.git .

# 如果是私有仓库，需要输入用户名和密码/Token
```

### 步骤 2: 配置环境变量

```bash
# 复制环境变量模板
sudo cp .env.example .env

# 编辑环境变量
sudo nano .env
```

**重要配置项**（修改以下值）：

```bash
# 数据库配置
DB_PASSWORD=你的强密码_修改这里
SECRET_KEY=你的密钥_修改这里
```

### 步骤 3: 修改 docker-compose.yml 密码

```bash
sudo nano docker-compose.yml
```

修改 MySQL 密码部分。

### 步骤 4: 启动服务

```bash
# 给脚本添加执行权限
sudo chmod +x deploy.sh

# 启动所有服务
sudo ./deploy.sh start
```

### 步骤 5: 查看服务状态

```bash
# 查看状态
sudo ./deploy.sh status

# 查看日志
sudo ./deploy.sh logs
```

### 步骤 6: 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 步骤 7: 访问应用

浏览器访问: `http://your_server_ip`

默认管理员: admin / admin123

---

## ❓ 常见问题

### 1. 端口被占用

```bash
# 查看端口占用
sudo netstat -tlnp | grep :80
sudo lsof -i :80

# 停止占用端口的服务
sudo systemctl stop apache2  # Ubuntu
sudo systemctl stop httpd    # CentOS
```

### 2. 容器无法启动

```bash
# 查看详细日志
sudo docker-compose logs web
sudo docker-compose logs mysql

# 重新构建
sudo ./deploy.sh build
sudo ./deploy.sh restart
```

### 3. 数据库连接失败

检查 .env 和 docker-compose.yml 中的密码是否一致。

### 4. 权限问题

```bash
# 修改目录权限
sudo chown -R $USER:$USER /opt/flask-app
```

---

## 🔧 维护管理

### 日常命令

```bash
# 重启服务
sudo ./deploy.sh restart

# 停止服务
sudo ./deploy.sh stop

# 查看日志
sudo ./deploy.sh logs

# 备份数据库
sudo ./deploy.sh backup
```

### 代码更新

```bash
cd /opt/flask-app

# 拉取最新代码
sudo git pull origin main

# 重启服务
sudo ./deploy.sh restart
```

### 数据库备份

```bash
# 手动备份
sudo ./deploy.sh backup

# 定时备份（添加到 crontab）
0 2 * * * cd /opt/flask-app && ./deploy.sh backup
```

---

## 📝 快速部署清单

- [ ] 创建 GitHub 仓库并推送代码
- [ ] 购买云服务器并连接
- [ ] 安装 Docker 和 Docker Compose
- [ ] 克隆代码到服务器
- [ ] 配置 .env 环境变量
- [ ] 修改 docker-compose.yml 密码
- [ ] 启动服务
- [ ] 配置防火墙
- [ ] 访问并测试应用
- [ ] 修改默认管理员密码

---

## 🚀 完成！

现在你的 Flask 应用已经成功部署在 Docker 容器中！
