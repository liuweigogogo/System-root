# 📋 部署检查清单

使用这个清单确保每一步都正确完成。

---

## 阶段一：准备工作 ✅

- [ ] 代码已完成开发和本地测试
- [ ] 已注册 GitHub 账号
- [ ] 已购买云服务器（推荐配置：2核4G）
- [ ] 获得服务器 SSH 登录信息
- [ ] 记录服务器 IP 地址：`___________________`

---

## 阶段二：GitHub 代码托管 ✅

- [ ] 在 GitHub 创建新仓库
- [ ] 仓库名称：`flask-file-converter`
- [ ] 本地项目已初始化 Git
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  ```
- [ ] 关联远程仓库
  ```bash
  git remote add origin https://github.com/你的用户名/仓库名.git
  ```
- [ ] 推送代码到 GitHub
  ```bash
  git push -u origin main
  ```
- [ ] 验证：访问 GitHub 确认代码已上传 ✓

---

## 阶段三：云服务器环境配置 ✅

### 3.1 连接服务器
- [ ] SSH 连接成功
  ```bash
  ssh root@服务器IP
  ```

### 3.2 更新系统
- [ ] 系统更新完成
  ```bash
  # Ubuntu/Debian
  sudo apt update && sudo apt upgrade -y
  
  # CentOS
  sudo yum update -y
  ```

### 3.3 安装 Docker
- [ ] Docker 安装完成
  ```bash
  curl -fsSL https://get.docker.com | sh
  ```
- [ ] Docker 服务启动
  ```bash
  sudo systemctl start docker
  sudo systemctl enable docker
  ```
- [ ] 验证 Docker 版本
  ```bash
  docker --version
  ```
  版本号：`___________________`

### 3.4 安装 Docker Compose
- [ ] Docker Compose 安装完成
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```
- [ ] 验证 Docker Compose 版本
  ```bash
  docker-compose --version
  ```
  版本号：`___________________`

### 3.5 安装 Git
- [ ] Git 安装完成
  ```bash
  # Ubuntu/Debian
  sudo apt install -y git
  
  # CentOS
  sudo yum install -y git
  ```

---

## 阶段四：部署应用 ✅

### 4.1 克隆代码
- [ ] 创建项目目录
  ```bash
  sudo mkdir -p /opt/flask-app
  cd /opt/flask-app
  ```
- [ ] 克隆代码成功
  ```bash
  sudo git clone https://github.com/你的用户名/仓库名.git .
  ```
- [ ] 验证：检查文件是否存在
  ```bash
  ls -la
  ```

### 4.2 配置环境变量
- [ ] 复制环境变量模板
  ```bash
  sudo cp .env.example .env
  ```
- [ ] 编辑 .env 文件
  ```bash
  sudo nano .env
  ```
- [ ] 已修改以下配置项：
  - [ ] `DB_PASSWORD`（数据库密码）
  - [ ] `SECRET_KEY`（Flask密钥）
  - [ ] 其他必要配置

**记录你的配置：**
- 数据库密码：`___________________`
- SECRET_KEY：`___________________`

### 4.3 配置 Docker Compose
- [ ] 编辑 docker-compose.yml
  ```bash
  sudo nano docker-compose.yml
  ```
- [ ] 已修改 MySQL 密码：
  - [ ] `MYSQL_ROOT_PASSWORD`
  - [ ] `MYSQL_PASSWORD`
- [ ] 确认密码与 .env 中的一致 ✓

### 4.4 启动服务
- [ ] 添加脚本执行权限
  ```bash
  sudo chmod +x deploy.sh
  ```
- [ ] 启动所有容器
  ```bash
  sudo ./deploy.sh start
  ```
- [ ] 等待服务启动（约30秒）
- [ ] 检查容器状态
  ```bash
  sudo docker-compose ps
  ```
- [ ] 确认所有容器状态为 "Up" ✓

### 4.5 查看日志
- [ ] 查看应用日志
  ```bash
  sudo ./deploy.sh logs
  ```
- [ ] 确认没有错误信息 ✓

---

## 阶段五：网络配置 ✅

### 5.1 配置防火墙
- [ ] 开放 HTTP 端口（80）
- [ ] 开放 HTTPS 端口（443）
- [ ] 开放 Flask 端口（5000，可选）

**Ubuntu/Debian:**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

**CentOS:**
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

### 5.2 云服务商安全组
- [ ] 在云服务商控制台开放端口：
  - [ ] 80（HTTP）
  - [ ] 443（HTTPS）
  - [ ] 5000（可选，开发调试用）

---

## 阶段六：测试验证 ✅

### 6.1 访问测试
- [ ] 浏览器访问：`http://你的服务器IP`
- [ ] 页面正常加载 ✓
- [ ] 登录页面显示正常 ✓

### 6.2 功能测试
- [ ] 使用默认账户登录
  - 用户名：`admin`
  - 密码：`admin123`
- [ ] 登录成功 ✓
- [ ] Dashboard 正常显示 ✓
- [ ] 用户管理功能正常 ✓
- [ ] 文件转换功能正常 ✓

### 6.3 数据库测试
- [ ] 进入 MySQL 容器
  ```bash
  sudo docker-compose exec mysql mysql -u root -p
  ```
- [ ] 查看数据库
  ```sql
  SHOW DATABASES;
  USE file_converter;
  SHOW TABLES;
  SELECT * FROM users;
  ```
- [ ] 数据正常 ✓

### 6.4 Redis 测试
- [ ] 进入 Redis 容器
  ```bash
  sudo docker-compose exec redis redis-cli
  ```
- [ ] 测试连接
  ```
  PING
  ```
- [ ] 返回 PONG ✓

---

## 阶段七：安全加固 ✅

- [ ] 修改默认管理员密码
- [ ] 禁用 root SSH 登录（可选）
- [ ] 配置 SSH 密钥登录（推荐）
- [ ] 定期更新系统和 Docker 镜像
- [ ] 配置 SSL 证书（生产环境必需）
- [ ] 设置数据库定时备份

---

## 阶段八：监控和维护 ✅

### 8.1 设置定时备份
- [ ] 创建备份脚本
  ```bash
  sudo crontab -e
  ```
- [ ] 添加定时任务
  ```
  0 2 * * * cd /opt/flask-app && ./deploy.sh backup
  ```

### 8.2 日志管理
- [ ] 配置日志轮转
- [ ] 设置日志保留期限

### 8.3 监控设置
- [ ] 监控服务器资源（CPU、内存、磁盘）
- [ ] 监控应用状态
- [ ] 设置告警通知

---

## 常用命令速查 📝

```bash
# 进入项目目录
cd /opt/flask-app

# 查看服务状态
sudo ./deploy.sh status

# 查看日志
sudo ./deploy.sh logs

# 重启服务
sudo ./deploy.sh restart

# 停止服务
sudo ./deploy.sh stop

# 启动服务
sudo ./deploy.sh start

# 更新代码
sudo git pull origin main
sudo ./deploy.sh restart

# 备份数据库
sudo ./deploy.sh backup

# 进入容器
sudo docker-compose exec web bash
sudo docker-compose exec mysql bash
sudo docker-compose exec redis bash
```

---

## 故障排查清单 🔧

### 问题：容器无法启动
- [ ] 检查端口是否被占用
  ```bash
  sudo netstat -tlnp | grep :80
  ```
- [ ] 查看容器日志
  ```bash
  sudo docker-compose logs
  ```
- [ ] 重新构建镜像
  ```bash
  sudo ./deploy.sh build
  ```

### 问题：数据库连接失败
- [ ] 确认 .env 中的密码正确
- [ ] 确认 docker-compose.yml 中的密码正确
- [ ] 两者密码是否一致
- [ ] MySQL 容器是否正常运行

### 问题：无法访问网页
- [ ] 检查防火墙规则
- [ ] 检查云服务商安全组
- [ ] 检查 Nginx 容器状态
- [ ] 检查 Flask 容器状态

---

## 部署完成确认 ✅

完成以下所有项目即表示部署成功：

- [ ] 所有容器正常运行
- [ ] 网页可以正常访问
- [ ] 登录功能正常
- [ ] 核心功能测试通过
- [ ] 数据库连接正常
- [ ] Redis 缓存正常
- [ ] 防火墙配置完成
- [ ] 安全加固完成
- [ ] 备份策略已设置
- [ ] 管理员密码已修改

---

## 重要信息记录 📋

**服务器信息：**
- IP 地址：`___________________`
- SSH 端口：`___________________`
- 操作系统：`___________________`

**应用信息：**
- 访问地址：`http://___________________`
- 管理员账户：`___________________`
- 数据库密码：`___________________`（请安全保管）

**部署日期：**
- 首次部署：`___________________`
- 最后更新：`___________________`

---

## 🎉 恭喜！部署完成！

你的 Flask 应用现已成功部署在 Docker 容器中！

**下一步建议：**
1. 配置域名和 HTTPS
2. 设置监控和告警
3. 优化性能和安全性
4. 阅读维护文档

需要帮助？查看 [README_DEPLOYMENT.md](./README_DEPLOYMENT.md)
