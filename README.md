# 🚀 Flask 文件转换系统

一个功能完善的文件转换和用户管理系统，基于 Flask + MySQL + Redis 架构，支持 Docker 一键部署。

---

## ✨ 主要功能

### 🔐 用户管理
- 用户注册、登录、注销
- 基于角色的权限控制（管理员/普通用户）
- 会话管理和安全认证
- 用户信息的增删改查

### 📄 文件转换
- 支持多种文件格式转换
- 文件上传和下载
- 转换历史记录
- 批量转换支持

### 📊 系统管理
- 系统日志查看
- 用户权限管理
- 统计数据展示
- 仪表板监控

### 🎨 界面特性
- 响应式设计
- 现代化 UI
- 多标签页管理
- 实时数据更新

---

## 🏗️ 技术架构

### 后端技术栈
- **Flask 2.3.3** - Web 框架
- **MySQL 8.0** - 关系型数据库
- **Redis 7** - 缓存和会话存储
- **bcrypt** - 密码加密
- **python-docx, pdf2docx** - 文件转换

### 前端技术栈
- **HTML5 + CSS3** - 页面结构和样式
- **Vanilla JavaScript** - 交互逻辑
- **Fetch API** - 异步请求

### 部署技术
- **Docker** - 容器化
- **Docker Compose** - 多容器编排
- **Nginx** - 反向代理
- **Linux** - 生产环境

---

## 📦 项目结构

```
project-root/
├── frotend/                    # 应用主目录
│   ├── app.py                  # Flask 应用入口
│   ├── requirements.txt        # Python 依赖
│   ├── config/                 # 配置文件
│   │   └── DatabaseSchema.py   # 数据库架构
│   ├── controllers/            # 控制器层
│   │   ├── AuthController.py
│   │   └── UserManagementController.py
│   ├── services/               # 服务层
│   │   ├── AuthService.py
│   │   └── UserManagementService.py
│   ├── model/                  # 模型层
│   │   └── BaseUser.py
│   ├── templates/              # HTML 模板
│   │   ├── login.html
│   │   └── dashboard.html
│   ├── js/                     # JavaScript 文件
│   │   ├── dashboard.js
│   │   ├── tabs.js
│   │   └── user_management.js
│   └── logs/                   # 日志目录
│
├── nginx/                      # Nginx 配置
│   └── nginx.conf
│
├── Dockerfile                  # Docker 镜像配置
├── docker-compose.yml          # Docker Compose 编排
├── deploy.sh                   # 部署脚本
├── init.sql                    # 数据库初始化脚本
├── .env.example                # 环境变量模板
├── .gitignore                  # Git 忽略文件
├── .dockerignore               # Docker 忽略文件
│
└── 📚 文档/
    ├── README.md               # 本文件
    ├── README_DEPLOYMENT.md    # 详细部署指南
    ├── QUICK_DEPLOY.md         # 快速部署（5分钟）
    ├── DEPLOYMENT_CHECKLIST.md # 部署检查清单
    ├── DOCKER_ARCHITECTURE.md  # Docker 架构说明
    └── FAQ.md                  # 常见问题解答
```

---

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

**只需 3 步，5 分钟部署完成！**

#### 1. 克隆代码到服务器

```bash
git clone https://github.com/你的用户名/flask-file-converter.git
cd flask-file-converter
```

#### 2. 配置环境变量

```bash
cp .env.example .env
nano .env
# 修改数据库密码和 SECRET_KEY
```

#### 3. 一键启动

```bash
chmod +x deploy.sh
./deploy.sh start
```

**完成！** 访问 `http://服务器IP` 即可使用。

👉 **详细步骤请查看**: [快速部署指南](./QUICK_DEPLOY.md)

---

### 方式二：本地开发

#### 1. 安装依赖

```bash
cd frotend
pip install -r requirements.txt
```

#### 2. 配置数据库

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE file_converter;

# 导入初始化脚本
mysql -u root -p file_converter < ../init.sql
```

#### 3. 配置环境变量

```bash
# 编辑 config/DatabaseConfig.py
# 修改数据库连接信息
```

#### 4. 启动应用

```bash
python app.py
```

访问 `http://localhost:5000`

---

## 📖 完整文档

### 📋 部署相关
- **[完整部署指南](./README_DEPLOYMENT.md)** - 从零开始部署到云服务器
- **[快速部署（5分钟）](./QUICK_DEPLOY.md)** - 最快速的部署方式
- **[部署检查清单](./DEPLOYMENT_CHECKLIST.md)** - 确保每一步都正确

### 🏗️ 架构相关
- **[Docker 架构说明](./DOCKER_ARCHITECTURE.md)** - 理解容器架构和网络

### ❓ 帮助文档
- **[常见问题解答](./FAQ.md)** - 35+ 常见问题和解决方案

---

## 🔧 配置说明

### 环境变量 (.env)

```bash
# 数据库配置
DB_HOST=mysql
DB_PORT=3306
DB_USER=flask_user
DB_PASSWORD=your_strong_password  # 必改
DB_NAME=file_converter

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379

# Flask 配置
SECRET_KEY=your_secret_key_here   # 必改
DEBUG=False

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=5000
```

### 默认账户

- **用户名**: `admin`
- **密码**: `admin123`

⚠️ **重要**: 首次登录后请立即修改默认密码！

---

## 🐳 Docker 服务

部署后会启动 4 个容器：

| 服务 | 端口 | 说明 |
|------|------|------|
| **Nginx** | 80, 443 | Web 服务器/反向代理 |
| **Flask** | 5000 | 应用服务器 |
| **MySQL** | 3306 | 数据库 |
| **Redis** | 6379 | 缓存服务 |

### 常用命令

```bash
# 查看服务状态
./deploy.sh status

# 查看日志
./deploy.sh logs

# 重启服务
./deploy.sh restart

# 停止服务
./deploy.sh stop

# 备份数据库
./deploy.sh backup
```

---

## 📊 数据库架构

### users（用户表）
- `id` - 用户 ID
- `username` - 用户名
- `password_hash` - 密码哈希
- `email` - 邮箱
- `role` - 角色（user/admin）
- `is_active` - 是否激活
- `created_at` - 创建时间
- `last_login` - 最后登录时间

### sessions（会话表）
- `id` - 会话 ID
- `user_id` - 用户 ID
- `session_token` - 会话令牌
- `ip_address` - IP 地址
- `expires_at` - 过期时间

### conversion_history（转换历史）
- `id` - 记录 ID
- `user_id` - 用户 ID
- `original_filename` - 原始文件名
- `converted_filename` - 转换后文件名
- `source_format` - 源格式
- `target_format` - 目标格式
- `status` - 状态

### system_logs（系统日志）
- `id` - 日志 ID
- `log_level` - 日志级别
- `message` - 日志内容
- `user_id` - 用户 ID
- `created_at` - 创建时间

---

## 🔐 安全特性

- ✅ 密码 bcrypt 加密
- ✅ 会话令牌验证
- ✅ CSRF 保护
- ✅ SQL 注入防护
- ✅ XSS 防护
- ✅ 基于角色的访问控制
- ✅ 登录失败限制
- ✅ 会话过期机制

---

## 🎯 API 接口

### 认证相关
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户注销
- `GET /api/check-auth` - 检查认证状态

### 用户管理（需要管理员权限）
- `GET /api/users` - 获取用户列表
- `GET /api/users/<id>` - 获取用户详情
- `POST /api/users` - 创建用户
- `PUT /api/users/<id>` - 更新用户
- `DELETE /api/users/<id>` - 删除用户
- `GET /api/users/statistics` - 用户统计

---

## 🛠️ 维护和更新

### 代码更新

```bash
cd /opt/flask-app
git pull origin main
./deploy.sh restart
```

### 数据备份

```bash
# 自动备份（推荐）
crontab -e
# 添加：0 2 * * * cd /opt/flask-app && ./deploy.sh backup

# 手动备份
./deploy.sh backup
```

### 日志查看

```bash
# 实时日志
./deploy.sh logs

# 应用日志
tail -f logs/app.log

# Nginx 日志
docker-compose exec nginx tail -f /var/log/nginx/access.log
```

---

## 📈 性能优化

### 推荐配置

**生产环境：**
- 使用 Gunicorn/uWSGI 替代 Flask 自带服务器
- 启用 Redis 缓存
- 配置 Nginx 缓存和 Gzip 压缩
- 使用 CDN 加速静态资源
- 数据库索引优化

**扩展性：**
- 支持水平扩展（多个 Flask 实例）
- Redis 主从复制
- MySQL 读写分离
- 负载均衡

---

## 🌟 特性亮点

- ✨ **开箱即用** - Docker 一键部署
- 🔒 **安全可靠** - 多层安全防护
- 🚀 **高性能** - Redis 缓存加速
- 📱 **响应式** - 支持移动端访问
- 🔧 **易维护** - 完整的日志和监控
- 📚 **文档完善** - 详细的部署和使用文档
- 🐳 **容器化** - 跨平台部署
- 🔄 **易扩展** - 模块化设计

---

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📝 版本历史

- **v1.0.0** (2025-01-16)
  - 初始版本发布
  - 用户认证系统
  - 文件转换功能
  - Docker 部署支持

---

## ⚠️ 注意事项

1. **生产环境必须**：
   - 修改默认管理员密码
   - 配置强密码策略
   - 启用 HTTPS
   - 配置防火墙
   - 定期备份数据

2. **安全建议**：
   - 不要将 `.env` 提交到 Git
   - 定期更新系统和依赖
   - 监控异常登录
   - 限制管理员账户数量

3. **性能建议**：
   - 定期清理日志
   - 优化数据库查询
   - 使用 CDN
   - 配置缓存策略

---

## 📞 获取帮助

遇到问题？查看以下资源：

1. **[常见问题解答](./FAQ.md)** - 35+ 常见问题
2. **[部署指南](./README_DEPLOYMENT.md)** - 详细部署步骤
3. **GitHub Issues** - 提交 bug 或功能请求
4. **查看日志** - `./deploy.sh logs`

---

## 📄 许可证

本项目仅供学习和研究使用。

---

## 🙏 致谢

感谢以下开源项目：

- [Flask](https://flask.palletsprojects.com/)
- [MySQL](https://www.mysql.com/)
- [Redis](https://redis.io/)
- [Docker](https://www.docker.com/)
- [Nginx](https://nginx.org/)

---

## 📚 快速链接

- 📖 [完整部署指南](./README_DEPLOYMENT.md)
- ⚡ [5分钟快速部署](./QUICK_DEPLOY.md)
- ✅ [部署检查清单](./DEPLOYMENT_CHECKLIST.md)
- 🏗️ [Docker 架构说明](./DOCKER_ARCHITECTURE.md)
- ❓ [常见问题解答](./FAQ.md)

---

<p align="center">
  <strong>⭐ 如果这个项目对你有帮助，请给个 Star！⭐</strong>
</p>

<p align="center">
  Made with ❤️ by Your Team
</p>
