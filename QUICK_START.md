# 🚀 快速开始指南

## 一键启动脚本

### Windows用户

创建 `start_dev.bat` 文件：

```batch
@echo off
echo ====================================
echo 文件转换系统 - 开发环境启动
echo ====================================

echo.
echo [1/4] 启动MySQL服务...
net start MySQL

echo.
echo [2/4] 启动Redis服务...
start "" "C:\Program Files\Redis\redis-server.exe"
timeout /t 2 /nobreak >nul

echo.
echo [3/4] 启动Flask后端...
cd frotend
start "" python app.py
cd ..

echo.
echo [4/4] 启动Vue前端...
cd frontend-vue
start "" npm run dev

echo.
echo ====================================
echo 所有服务已启动！
echo.
echo Flask后端: http://localhost:5000
echo Vue前端: http://localhost:3000
echo ====================================
pause
```

### Linux/Mac用户

创建 `start_dev.sh` 文件：

```bash
#!/bin/bash

echo "===================================="
echo "文件转换系统 - 开发环境启动"
echo "===================================="

# 启动MySQL（如果需要）
echo -e "\n[1/4] 检查MySQL服务..."
sudo service mysql status || sudo service mysql start

# 启动Redis
echo -e "\n[2/4] 启动Redis服务..."
redis-server --daemonize yes

# 启动Flask后端
echo -e "\n[3/4] 启动Flask后端..."
cd frotend
source venv/bin/activate  # 如果使用虚拟环境
python app.py &
FLASK_PID=$!
cd ..

# 启动Vue前端
echo -e "\n[4/4] 启动Vue前端..."
cd frontend-vue
npm run dev &
VUE_PID=$!
cd ..

echo -e "\n===================================="
echo "所有服务已启动！"
echo ""
echo "Flask后端: http://localhost:5000"
echo "Vue前端: http://localhost:3000"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "===================================="

# 等待用户中断
trap "kill $FLASK_PID $VUE_PID; exit" INT
wait
```

赋予执行权限：
```bash
chmod +x start_dev.sh
./start_dev.sh
```

---

## 分步启动

如果自动脚本不工作，可以手动逐步启动：

### 步骤1: 启动MySQL

```bash
# Windows
net start MySQL

# Linux
sudo service mysql start

# Mac
brew services start mysql
```

### 步骤2: 启动Redis

```bash
# Windows
redis-server

# Linux
sudo service redis-server start

# Mac
brew services start redis
```

### 步骤3: 启动Flask后端

```bash
# 进入后端目录
cd frotend

# 激活虚拟环境（如果有）
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 启动Flask
python app.py
```

后端将在 `http://localhost:5000` 运行

### 步骤4: 启动Vue前端

**打开新的终端窗口**

```bash
# 进入前端目录
cd frontend-vue

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:3000` 运行

---

## 首次使用配置

### 1. 数据库初始化

```bash
cd frotend
python setup_db.py
```

这将创建必要的数据库表：
- `users` - 用户表
- `user_sessions` - 会话表

### 2. 测试账号（可选）

运行初始化脚本后，可以使用以下测试账号登录：

```
用户名: admin
密码: admin123
```

或者直接在注册页面注册新账号。

### 3. Redis配置检查

确保Redis配置正确：

```bash
# 测试Redis连接
redis-cli ping
# 应该返回 PONG
```

如果Redis需要密码，编辑 `frotend/config/RedisConfig.py`：

```python
REDIS_PASSWORD = 'your_password'
```

---

## 开发工具推荐

### VS Code扩展

后端开发：
- Python
- Pylance
- Python Docstring Generator

前端开发：
- Volar (Vue 3)
- TypeScript Vue Plugin
- ESLint
- Prettier

### PyCharm配置

1. 打开项目
2. 配置Python解释器（选择虚拟环境）
3. 启用TypeScript支持（Settings > Languages & Frameworks > TypeScript）

---

## 常用命令

### 后端

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py

# 运行测试
python test_system.py

# 查看日志
cat logs/app.log
```

### 前端

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build

# 预览构建产物
npm run preview

# 代码检查
npm run lint
```

---

## 调试技巧

### 后端调试

#### 1. 使用Python调试器

```python
# 在需要调试的地方添加断点
import pdb; pdb.set_trace()

# 或使用ipdb（需要安装：pip install ipdb）
import ipdb; ipdb.set_trace()
```

#### 2. 查看日志

日志文件位于 `logs/` 目录：
- `app.log` - 应用主日志
- `auth.log` - 认证日志
- `database.log` - 数据库日志
- `error.log` - 错误日志

### 前端调试

#### 1. 浏览器开发者工具

- **F12** 打开开发者工具
- **Console** 查看日志
- **Network** 查看API请求
- **Vue DevTools** 查看组件状态

#### 2. VS Code调试

创建 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend-vue/src"
    }
  ]
}
```

---

## 故障排除

### 问题1: 端口占用

```bash
# Windows查看端口占用
netstat -ano | findstr :5000
taskkill /F /PID <PID>

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### 问题2: 模块导入错误

```bash
# 确保在正确的目录
cd frotend

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 问题3: 前端npm安装失败

```bash
# 清除缓存
npm cache clean --force

# 删除node_modules和package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 如果还是失败，尝试使用yarn
npm install -g yarn
yarn install
```

### 问题4: Redis连接超时

```bash
# 检查Redis是否运行
redis-cli ping

# 如果没有运行，启动Redis
redis-server

# 检查Redis配置
redis-cli config get requirepass
```

---

## 性能监控

### 后端性能

查看日志中的执行时间：

```bash
# 查看数据库操作耗时
grep "执行时间" logs/database.log

# 查看登录耗时
grep "登录耗费时间" logs/app.log
```

### 前端性能

使用浏览器的Performance工具：
1. F12打开开发者工具
2. 切换到Performance标签
3. 点击Record，进行操作后Stop
4. 分析性能报告

### Redis缓存命中率

```bash
# 连接到Redis
redis-cli

# 查看统计信息
INFO stats

# 查看缓存键
KEYS session:*
```

---

## 生产环境部署

### 使用Docker（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: self_system
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    
  backend:
    build: ./frotend
    ports:
      - "5000:5000"
    depends_on:
      - mysql
      - redis
    environment:
      MYSQL_HOST: mysql
      REDIS_HOST: redis

  frontend:
    build: ./frontend-vue
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mysql_data:
```

启动：
```bash
docker-compose up -d
```

### 使用传统方式

#### 后端（使用Gunicorn）

```bash
# 安装Gunicorn
pip install gunicorn

# 启动
cd frotend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 前端（使用Nginx）

```bash
# 构建前端
cd frontend-vue
npm run build

# 配置Nginx
# /etc/nginx/sites-available/file-converter
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/frontend-vue/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 进阶配置

### 配置HTTPS

使用Let's Encrypt免费证书：

```bash
sudo certbot --nginx -d your-domain.com
```

### 配置CDN

将前端静态资源上传到CDN，修改 `vite.config.ts`：

```typescript
export default defineConfig({
  base: 'https://cdn.your-domain.com/',
  // ...
})
```

### 配置监控

使用Prometheus + Grafana监控系统性能。

---

## 获取帮助

- 📖 查看详细文档：`README_REFACTORED.md`
- 🐛 报告问题：提交Issue
- 💬 讨论：参与Discussions

祝您使用愉快！🎉
