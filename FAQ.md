# ❓ 常见问题解答 (FAQ)

## 📑 目录

- [部署相关](#部署相关)
- [容器问题](#容器问题)
- [数据库问题](#数据库问题)
- [网络访问](#网络访问)
- [性能优化](#性能优化)
- [安全相关](#安全相关)
- [维护管理](#维护管理)

---

## 部署相关

### Q1: Docker 和 Docker Compose 有什么区别？

**A:** 
- **Docker**: 容器运行时，负责运行单个容器
- **Docker Compose**: 编排工具，可以同时管理多个容器

我们的项目需要 4 个容器（Nginx、Flask、MySQL、Redis），使用 Docker Compose 可以一键启动所有服务。

---

### Q2: 我的云服务器配置应该选多大？

**A:** 最低配置建议：

| 用途 | CPU | 内存 | 硬盘 | 带宽 |
|-----|-----|------|------|------|
| 测试环境 | 1核 | 2GB | 20GB | 1Mbps |
| **推荐配置** | **2核** | **4GB** | **40GB** | **3Mbps** |
| 生产环境 | 4核 | 8GB | 100GB | 5Mbps+ |

---

### Q3: 支持哪些 Linux 发行版？

**A:** 支持所有主流 Linux 发行版：

✅ Ubuntu 18.04+  
✅ Debian 9+  
✅ CentOS 7+  
✅ Fedora 30+  
✅ Amazon Linux 2  

**推荐使用 Ubuntu 20.04 LTS** - 最稳定，文档最全。

---

### Q4: 可以在 Windows 服务器上部署吗？

**A:** 可以，但不推荐：

- 需要安装 Docker Desktop for Windows
- 性能比 Linux 差
- 配置更复杂
- 成本更高

**强烈建议使用 Linux 服务器。**

---

### Q5: GitHub 私有仓库如何克隆？

**A:** 两种方法：

**方法 1: 使用 Personal Access Token**
```bash
git clone https://TOKEN@github.com/username/repo.git
```

**方法 2: 配置 SSH 密钥**
```bash
# 生成密钥
ssh-keygen -t rsa -b 4096

# 添加到 GitHub
cat ~/.ssh/id_rsa.pub
# 复制内容到 GitHub Settings → SSH Keys

# 克隆仓库
git clone git@github.com:username/repo.git
```

---

## 容器问题

### Q6: 容器启动失败怎么办？

**A:** 按以下步骤排查：

```bash
# 1. 查看容器状态
docker-compose ps

# 2. 查看详细日志
docker-compose logs

# 3. 查看特定容器日志
docker-compose logs web
docker-compose logs mysql

# 4. 检查端口占用
netstat -tlnp | grep :80
netstat -tlnp | grep :3306

# 5. 重新启动
docker-compose down
docker-compose up -d
```

---

### Q7: 提示 "端口已被占用" 怎么办？

**A:** 

**检查占用进程：**
```bash
# 查看端口 80
sudo lsof -i :80
# 或
sudo netstat -tlnp | grep :80
```

**解决方法：**

**方法 1: 停止占用进程**
```bash
# Ubuntu
sudo systemctl stop apache2
sudo systemctl stop nginx

# CentOS
sudo systemctl stop httpd
```

**方法 2: 修改端口映射**
```yaml
# 修改 docker-compose.yml
services:
  nginx:
    ports:
      - "8080:80"  # 改用 8080 端口
```

---

### Q8: MySQL 容器一直重启？

**A:** 常见原因：

**1. 内存不足**
```bash
# 检查内存
free -h

# 如果内存小于 2GB，调整 MySQL 配置
# 在 docker-compose.yml 中添加：
environment:
  - MYSQL_INNODB_BUFFER_POOL_SIZE=128M
```

**2. 数据损坏**
```bash
# 删除数据卷重新初始化
docker-compose down -v
docker-compose up -d
```

**3. 权限问题**
```bash
# 修复权限
sudo chown -R 999:999 mysql_data/
```

---

### Q9: 如何进入容器内部？

**A:** 

```bash
# 进入 Flask 容器
docker-compose exec web bash

# 进入 MySQL 容器
docker-compose exec mysql bash

# 进入 Redis 容器
docker-compose exec redis sh

# 进入 Nginx 容器
docker-compose exec nginx sh
```

---

### Q10: 如何查看容器资源使用情况？

**A:** 

```bash
# 实时监控所有容器
docker stats

# 查看特定容器
docker stats flask_app
```

---

## 数据库问题

### Q11: 忘记数据库密码怎么办？

**A:** 

```bash
# 方法 1: 查看 .env 文件
cat .env | grep DB_PASSWORD

# 方法 2: 查看 docker-compose.yml
cat docker-compose.yml | grep MYSQL_PASSWORD

# 方法 3: 重置密码（会清空数据）
docker-compose down -v
# 修改密码后重新启动
docker-compose up -d
```

---

### Q12: 如何连接到 MySQL 数据库？

**A:** 

**从容器内连接：**
```bash
docker-compose exec mysql mysql -u root -p
# 输入密码后进入 MySQL
```

**从宿主机连接：**
```bash
mysql -h 127.0.0.1 -P 3306 -u flask_user -p
```

**使用客户端工具（Navicat/DBeaver）：**
- Host: `服务器IP`
- Port: `3306`
- Username: `flask_user`
- Password: `你的密码`
- Database: `file_converter`

---

### Q13: 如何备份和恢复数据库？

**A:** 

**备份：**
```bash
# 方法 1: 使用部署脚本
./deploy.sh backup

# 方法 2: 手动备份
docker-compose exec mysql mysqldump -u root -p file_converter > backup_$(date +%Y%m%d).sql

# 备份所有数据库
docker-compose exec mysql mysqldump -u root -p --all-databases > all_backup.sql
```

**恢复：**
```bash
# 恢复数据库
docker-compose exec -T mysql mysql -u root -p file_converter < backup.sql

# 或进入容器后恢复
docker-compose exec mysql bash
mysql -u root -p file_converter < /path/to/backup.sql
```

---

### Q14: 数据库连接数过多怎么办？

**A:** 

```bash
# 查看当前连接数
docker-compose exec mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# 增加最大连接数
# 在 docker-compose.yml 中添加：
command: --max_connections=500

# 重启服务
docker-compose restart mysql
```

---

## 网络访问

### Q15: 可以访问服务器 IP，但网页打不开？

**A:** 

**检查清单：**

1. **检查容器状态**
```bash
docker-compose ps
# 确保所有容器状态为 "Up"
```

2. **检查防火墙**
```bash
# Ubuntu
sudo ufw status
sudo ufw allow 80/tcp

# CentOS
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

3. **检查云服务商安全组**
   - 登录云服务商控制台
   - 安全组规则
   - 开放 80 端口（入站规则）

4. **测试端口连通性**
```bash
# 在本地电脑测试
telnet 服务器IP 80
# 或
curl http://服务器IP
```

---

### Q16: 如何配置域名访问？

**A:** 

**步骤 1: 域名解析**
- 登录域名提供商
- 添加 A 记录
- 指向服务器 IP

**步骤 2: 修改 Nginx 配置**
```bash
sudo nano nginx/nginx.conf
```

修改 `server_name`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    # ...
}
```

**步骤 3: 重启 Nginx**
```bash
docker-compose restart nginx
```

---

### Q17: 如何配置 HTTPS？

**A:** 

**方法 1: 使用 Let's Encrypt（免费）**

```bash
# 1. 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 2. 获取证书
sudo certbot --nginx -d yourdomain.com

# 3. 自动续期
sudo crontab -e
# 添加：
0 3 * * * certbot renew --quiet
```

**方法 2: 使用自己的证书**

```bash
# 1. 复制证书到服务器
mkdir -p nginx/ssl
cp cert.pem nginx/ssl/
cp key.pem nginx/ssl/

# 2. 修改 nginx.conf（取消 HTTPS 部分注释）

# 3. 重启
docker-compose restart nginx
```

---

### Q18: 如何限制访问 IP？

**A:** 

在 `nginx/nginx.conf` 中添加：

```nginx
server {
    # 只允许特定 IP 访问
    allow 1.2.3.4;
    allow 5.6.7.0/24;
    deny all;
    
    # ...
}
```

---

## 性能优化

### Q19: 网站访问速度慢怎么办？

**A:** 

**1. 启用 Gzip 压缩**（已在 nginx.conf 中配置）

**2. 优化数据库查询**
```bash
# 查看慢查询
docker-compose exec mysql mysql -u root -p -e "SHOW VARIABLES LIKE 'slow_query%';"
```

**3. 增加 Redis 缓存**
```python
# 在 Flask 中使用缓存
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})
```

**4. 使用 CDN**
- 将静态文件放到 CDN
- 加速图片、CSS、JS 加载

**5. 增加服务器资源**
- 升级 CPU/内存
- 使用 SSD 硬盘

---

### Q20: 如何扩展到多个 Flask 实例？

**A:** 

**方法 1: Docker Compose Scale**
```bash
docker-compose up -d --scale web=3
```

**方法 2: 修改 docker-compose.yml**
```yaml
services:
  web:
    deploy:
      replicas: 3
```

**同时需要配置 Nginx 负载均衡：**
```nginx
upstream flask_app {
    server web_1:5000;
    server web_2:5000;
    server web_3:5000;
}
```

---

## 安全相关

### Q21: 如何修改默认管理员密码？

**A:** 

**方法 1: 通过 Web 界面**
1. 登录系统
2. 进入用户管理
3. 编辑 admin 用户
4. 修改密码

**方法 2: 通过数据库**
```bash
# 生成新密码哈希
python3 -c "from bcrypt import hashpw, gensalt; print(hashpw(b'new_password', gensalt()).decode())"

# 进入 MySQL
docker-compose exec mysql mysql -u root -p

# 更新密码
USE file_converter;
UPDATE users SET password_hash='新生成的哈希' WHERE username='admin';
```

---

### Q22: 如何防止暴力破解？

**A:** 

**1. 限制登录尝试次数**（已在代码中实现）

**2. 使用 Nginx 限流**

在 `nginx/nginx.conf` 中添加：
```nginx
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;

location /api/login {
    limit_req zone=login_limit burst=2;
    proxy_pass http://flask_app;
}
```

**3. 使用 Fail2ban**
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

---

### Q23: 敏感信息（密码）如何保护？

**A:** 

✅ **正确做法：**
- 使用 `.env` 文件存储密码
- `.env` 添加到 `.gitignore`
- 生产环境使用环境变量或密钥管理服务

❌ **错误做法：**
- 密码硬编码在代码中
- 密码提交到 Git 仓库
- 使用简单密码

**生成强密码：**
```bash
# 生成 32 位随机密码
openssl rand -base64 32
```

---

## 维护管理

### Q24: 如何查看日志？

**A:** 

```bash
# 所有容器日志
docker-compose logs -f

# 特定容器日志
docker-compose logs -f web
docker-compose logs -f mysql

# 查看最近 100 行
docker-compose logs --tail=100

# Flask 应用日志
tail -f logs/app.log

# Nginx 访问日志
docker-compose exec nginx tail -f /var/log/nginx/access.log
```

---

### Q25: 如何更新代码？

**A:** 

```bash
# 1. 进入项目目录
cd /opt/flask-app

# 2. 备份当前版本（可选）
git tag backup-$(date +%Y%m%d)

# 3. 拉取最新代码
git pull origin main

# 4. 重新构建镜像（如果 Dockerfile 有变化）
docker-compose build

# 5. 重启服务
docker-compose down
docker-compose up -d

# 或使用部署脚本
./deploy.sh restart
```

---

### Q26: 如何清理 Docker 占用的磁盘空间？

**A:** 

```bash
# 查看磁盘使用
df -h
docker system df

# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune

# 一键清理所有（谨慎使用）
docker system prune -a --volumes
```

---

### Q27: 如何定时备份？

**A:** 

```bash
# 编辑定时任务
crontab -e

# 添加以下内容：

# 每天凌晨 2 点备份数据库
0 2 * * * cd /opt/flask-app && ./deploy.sh backup

# 每周日凌晨 3 点备份文件
0 3 * * 0 cd /opt/flask-app && tar -czf /backup/uploads_$(date +\%Y\%m\%d).tar.gz uploads/

# 删除 30 天前的备份
0 4 * * * find /backup -name "*.sql" -mtime +30 -delete
```

---

### Q28: 如何监控服务器资源？

**A:** 

**方法 1: 使用 htop**
```bash
sudo apt install htop
htop
```

**方法 2: 使用 Docker Stats**
```bash
docker stats
```

**方法 3: 使用监控工具**
- Prometheus + Grafana
- Zabbix
- Netdata

**快速安装 Netdata：**
```bash
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
# 访问 http://服务器IP:19999
```

---

### Q29: 如何回滚到之前的版本？

**A:** 

```bash
# 1. 查看提交历史
git log --oneline

# 2. 回滚到特定版本
git checkout <commit-hash>

# 或回滚到上一个版本
git checkout HEAD~1

# 3. 重启服务
docker-compose down
docker-compose up -d --build
```

---

### Q30: 服务突然停止怎么办？

**A:** 

**紧急处理步骤：**

```bash
# 1. 查看服务状态
docker-compose ps

# 2. 快速重启
docker-compose restart

# 3. 如果还是不行，完全重启
docker-compose down
docker-compose up -d

# 4. 查看错误日志
docker-compose logs --tail=50

# 5. 检查服务器资源
free -h  # 内存
df -h    # 磁盘
top      # CPU
```

---

## 其他问题

### Q31: 可以在本地 Windows 开发，服务器部署吗？

**A:** 

可以！推荐工作流程：

```
本地开发 (Windows) 
  ↓ git push
GitHub 仓库
  ↓ git pull
Linux 服务器 (Docker 部署)
```

**本地开发：**
- 使用 PyCharm/VS Code
- 使用 Python 虚拟环境
- 直接运行 Flask 应用

**服务器部署：**
- 使用 Docker Compose
- 自动化部署

---

### Q32: 数据会丢失吗？

**A:** 

**不会！** 只要你：

✅ 使用 Docker Volumes（已配置）  
✅ 定期备份数据库  
✅ 不执行 `docker-compose down -v`（-v 会删除数据卷）  

**安全操作：**
```bash
# 停止服务（保留数据）
docker-compose stop

# 重启服务（保留数据）
docker-compose restart
```

**危险操作：**
```bash
# 删除所有数据（谨慎！）
docker-compose down -v
```

---

### Q33: 需要域名吗？可以只用 IP 访问吗？

**A:** 

**可以只用 IP！**

- 开发/测试环境：直接用 IP 即可
- 生产环境：强烈建议使用域名
  - 更专业
  - 便于记忆
  - 可以配置 HTTPS

---

### Q34: 多个项目可以共用一个服务器吗？

**A:** 

可以！使用不同的端口：

**项目 1:**
```yaml
ports:
  - "80:80"  # 或 "8001:80"
```

**项目 2:**
```yaml
ports:
  - "8002:80"
```

**使用 Nginx 做统一入口：**
```nginx
# 项目 1
server {
    listen 80;
    server_name project1.com;
    location / {
        proxy_pass http://localhost:8001;
    }
}

# 项目 2
server {
    listen 80;
    server_name project2.com;
    location / {
        proxy_pass http://localhost:8002;
    }
}
```

---

### Q35: 遇到问题去哪里寻求帮助？

**A:** 

1. **查看文档**
   - [README_DEPLOYMENT.md](./README_DEPLOYMENT.md)
   - [QUICK_DEPLOY.md](./QUICK_DEPLOY.md)
   - [DOCKER_ARCHITECTURE.md](./DOCKER_ARCHITECTURE.md)

2. **查看日志**
   ```bash
   docker-compose logs
   ```

3. **搜索错误信息**
   - Google 搜索错误信息
   - Stack Overflow
   - Docker 官方文档

4. **社区帮助**
   - GitHub Issues
   - Docker 中文社区
   - Flask 中文社区

5. **检查配置**
   - 环境变量是否正确
   - 密码是否一致
   - 端口是否冲突

---

## 💡 小贴士

### 最佳实践

1. **定期备份** - 每天自动备份数据库
2. **监控日志** - 及时发现问题
3. **更新系统** - 定期更新软件包
4. **强密码** - 使用复杂密码
5. **限制权限** - 最小权限原则
6. **使用 HTTPS** - 生产环境必须
7. **定期更新代码** - 修复 bug 和安全漏洞

### 常用命令备忘

```bash
# 进入项目目录
cd /opt/flask-app

# 查看状态
./deploy.sh status

# 查看日志  
./deploy.sh logs

# 重启服务
./deploy.sh restart

# 备份数据
./deploy.sh backup

# 更新代码
git pull && docker-compose restart
```

---

**还有其他问题？** 

欢迎提交 Issue 或查看项目文档！

📚 [返回部署指南](./README_DEPLOYMENT.md)
