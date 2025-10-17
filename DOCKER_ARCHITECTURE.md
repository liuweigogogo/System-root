# 🏗️ Docker 部署架构说明

## 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        云服务器 Linux                              │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Docker Engine                         │    │
│  │                                                          │    │
│  │  ┌────────────────────────────────────────────────┐    │    │
│  │  │         Docker Network (flask_network)         │    │    │
│  │  │                                                 │    │    │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │    │    │
│  │  │  │  Nginx   │  │  Flask   │  │  MySQL   │    │    │    │
│  │  │  │ Container│←→│ Container│←→│ Container│    │    │    │
│  │  │  │  (80)    │  │  (5000)  │  │  (3306)  │    │    │    │
│  │  │  └────┬─────┘  └─────┬────┘  └────┬─────┘    │    │    │
│  │  │       │              │             │          │    │    │
│  │  │       │              │      ┌──────┴──────┐  │    │    │
│  │  │       │              │      │   Redis     │  │    │    │
│  │  │       │              └─────→│  Container  │  │    │    │
│  │  │       │                     │   (6379)    │  │    │    │
│  │  │       │                     └─────────────┘  │    │    │
│  │  │       │                                       │    │    │
│  │  └───────┼───────────────────────────────────────┘    │    │
│  │          │                                             │    │
│  └──────────┼─────────────────────────────────────────────┘    │
│             │                                                   │
│  ┌──────────┼─────────────────────────────────────────────┐    │
│  │          │        Docker Volumes (数据持久化)           │    │
│  │  ┌───────▼──────┬──────────────┬──────────────┐       │    │
│  │  │ mysql_data   │ redis_data   │ upload_data  │       │    │
│  │  └──────────────┴──────────────┴──────────────┘       │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            │ Port 80/443
                            │
                    ┌───────▼────────┐
                    │   Internet     │
                    │   用户访问      │
                    └────────────────┘
```

---

## 容器详细说明

### 1. Nginx 容器 (nginx)

**作用：** 反向代理和负载均衡

**端口映射：**
- `80:80` - HTTP
- `443:443` - HTTPS（可选）

**功能：**
- 接收外部 HTTP/HTTPS 请求
- 转发请求到 Flask 应用
- 处理静态文件（CSS、JS、图片）
- Gzip 压缩
- SSL/TLS 加密（生产环境）

**配置文件：** `nginx/nginx.conf`

**启动命令：**
```bash
docker-compose up -d nginx
```

---

### 2. Flask Web 容器 (web)

**作用：** 运行 Flask 应用主程序

**端口映射：**
- `5000:5000` - Flask 应用端口

**环境变量：**
- `DB_HOST=mysql` - 数据库主机
- `DB_PORT=3306` - 数据库端口
- `DB_USER` - 数据库用户
- `DB_PASSWORD` - 数据库密码
- `REDIS_HOST=redis` - Redis 主机
- `REDIS_PORT=6379` - Redis 端口

**挂载目录：**
- `./frotend:/app` - 应用代码
- `./logs:/app/logs` - 日志文件
- `upload_data:/app/uploads` - 上传文件

**依赖：**
- 等待 MySQL 容器健康检查通过
- 等待 Redis 容器健康检查通过

**Dockerfile：** `Dockerfile`

---

### 3. MySQL 容器 (mysql)

**作用：** 数据库存储

**端口映射：**
- `3306:3306` - MySQL 端口

**环境变量：**
- `MYSQL_ROOT_PASSWORD` - root 密码
- `MYSQL_DATABASE=file_converter` - 数据库名
- `MYSQL_USER=flask_user` - 应用用户
- `MYSQL_PASSWORD` - 应用用户密码

**数据持久化：**
- `mysql_data:/var/lib/mysql` - 数据库文件
- `./init.sql:/docker-entrypoint-initdb.d/init.sql` - 初始化脚本

**健康检查：**
```bash
mysqladmin ping -h localhost
```

**存储内容：**
- 用户表（users）
- 会话表（sessions）
- 转换历史（conversion_history）
- 系统日志（system_logs）

---

### 4. Redis 容器 (redis)

**作用：** 缓存和会话存储

**端口映射：**
- `6379:6379` - Redis 端口

**数据持久化：**
- `redis_data:/data` - Redis 数据文件

**健康检查：**
```bash
redis-cli ping
```

**用途：**
- 用户会话缓存
- API 响应缓存
- 临时数据存储
- 速率限制

---

## 网络架构

### Docker Network (flask_network)

**类型：** Bridge 网络

**作用：** 允许容器间相互通信

**容器通信：**
```
Nginx ←→ Flask Web
Flask Web ←→ MySQL
Flask Web ←→ Redis
```

**DNS 解析：**
- 容器名即为主机名
- `mysql` → MySQL 容器 IP
- `redis` → Redis 容器 IP
- `web` → Flask Web 容器 IP

---

## 数据持久化

### Volume 说明

| Volume 名称 | 挂载路径 | 用途 | 大小建议 |
|------------|---------|------|---------|
| `mysql_data` | `/var/lib/mysql` | MySQL 数据文件 | 5GB+ |
| `redis_data` | `/data` | Redis 数据文件 | 1GB+ |
| `upload_data` | `/app/uploads` | 用户上传文件 | 10GB+ |
| `./logs` (bind mount) | `/app/logs` | 应用日志 | 2GB+ |

### 数据备份

**备份命令：**
```bash
# 备份 MySQL
docker-compose exec mysql mysqldump -u root -p file_converter > backup.sql

# 备份文件
tar -czf uploads_backup.tar.gz uploads/

# 使用部署脚本
./deploy.sh backup
```

---

## 请求流程

### 用户访问流程

```
1. 用户浏览器
   ↓ (HTTP/HTTPS)
2. 云服务器防火墙 (端口 80/443)
   ↓
3. Nginx 容器 (端口 80)
   ↓ (反向代理)
4. Flask Web 容器 (端口 5000)
   ↓
5. 处理业务逻辑
   ├→ 查询 MySQL (端口 3306)
   └→ 查询 Redis (端口 6379)
   ↓
6. 返回响应
   ↓
7. Nginx 返回给用户
```

### 静态文件流程

```
1. 用户请求静态文件 (CSS/JS/图片)
   ↓
2. Nginx 容器
   ↓
3. 直接从 /app/static/ 读取
   ↓
4. 返回给用户（不经过 Flask）
```

---

## 端口映射表

| 服务 | 容器内端口 | 宿主机端口 | 协议 | 说明 |
|-----|----------|----------|------|------|
| Nginx | 80 | 80 | HTTP | Web 访问 |
| Nginx | 443 | 443 | HTTPS | 加密访问 |
| Flask | 5000 | 5000 | HTTP | 应用服务 |
| MySQL | 3306 | 3306 | TCP | 数据库 |
| Redis | 6379 | 6379 | TCP | 缓存 |

---

## 容器依赖关系

```
启动顺序：
1. MySQL    (先启动，等待健康检查)
2. Redis    (先启动，等待健康检查)
3. Flask    (依赖 MySQL 和 Redis)
4. Nginx    (依赖 Flask)
```

**健康检查确保：**
- MySQL 完全启动后才启动 Flask
- Redis 完全启动后才启动 Flask
- 避免连接失败

---

## 资源限制建议

### 生产环境资源配置

在 `docker-compose.yml` 中添加：

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
  
  mysql:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

---

## 扩展性考虑

### 水平扩展（多实例）

```yaml
services:
  web:
    deploy:
      replicas: 3  # 运行 3 个 Flask 实例
```

### 垂直扩展（增加资源）

- 增加服务器 CPU/内存
- 调整容器资源限制
- 优化数据库连接池

---

## 安全策略

### 1. 网络隔离

- 使用内部网络连接容器
- 只暴露必要端口（80/443）
- MySQL 和 Redis 不对外暴露

### 2. 数据加密

- 使用 SSL/TLS 证书
- 数据库密码加密存储
- 环境变量隔离

### 3. 访问控制

- Nginx 限流配置
- 防火墙规则
- 容器权限最小化

---

## 监控和日志

### 日志位置

```bash
# 容器日志
docker-compose logs -f

# Flask 应用日志
./logs/app.log

# Nginx 访问日志
docker-compose exec nginx cat /var/log/nginx/access.log

# MySQL 日志
docker-compose exec mysql tail -f /var/log/mysql/error.log
```

### 监控指标

- CPU 使用率
- 内存使用率
- 磁盘使用率
- 网络流量
- 请求响应时间
- 数据库连接数

---

## 故障恢复

### 自动重启策略

所有容器配置 `restart: always`：
- 容器崩溃自动重启
- 服务器重启后自动启动
- 确保服务高可用

### 数据恢复

```bash
# 恢复数据库
docker-compose exec mysql mysql -u root -p file_converter < backup.sql

# 恢复上传文件
tar -xzf uploads_backup.tar.gz
```

---

## 性能优化建议

### 1. 数据库优化
- 启用查询缓存
- 添加索引
- 定期清理日志

### 2. Redis 优化
- 设置内存限制
- 配置持久化策略
- 使用连接池

### 3. Nginx 优化
- 启用 Gzip 压缩
- 配置缓存策略
- 启用 HTTP/2

### 4. Flask 优化
- 使用 Gunicorn 多进程
- 启用缓存
- 优化数据库查询

---

## 总结

这个 Docker 架构提供了：

✅ **易部署** - 一键启动所有服务  
✅ **可移植** - 跨平台运行  
✅ **可扩展** - 支持水平和垂直扩展  
✅ **高可用** - 自动重启和健康检查  
✅ **易维护** - 日志集中管理  
✅ **安全性** - 网络隔离和访问控制  

**适用场景：**
- 开发环境快速搭建
- 测试环境部署
- 小型生产环境
- 个人项目托管

**不适用场景：**
- 超大规模集群（建议使用 Kubernetes）
- 需要复杂编排的微服务

---

需要帮助？查看：
- [部署指南](./README_DEPLOYMENT.md)
- [快速部署](./QUICK_DEPLOY.md)
- [检查清单](./DEPLOYMENT_CHECKLIST.md)
