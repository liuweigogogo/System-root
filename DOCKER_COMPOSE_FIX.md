# 🔧 Docker Compose 安装问题修复指南

## ❌ 错误原因

你遇到的错误是因为下载的 `docker-compose` 文件是一个 404 错误的 HTML 页面，而不是真正的可执行文件。

```
/usr/local/bin/docker-compose: line 1: html: No such file or directory
```

这通常是因为下载链接失效或网络问题导致的。

---

## ✅ 解决方案（按推荐顺序）

### 方案一：使用包管理器安装（最简单，推荐）

#### Ubuntu/Debian:
```bash
# 1. 删除错误的文件
sudo rm -f /usr/local/bin/docker-compose

# 2. 更新软件源
sudo apt update

# 3. 安装 Docker Compose 插件
sudo apt install docker-compose-plugin -y

# 4. 验证安装
docker compose version
```

#### CentOS/RHEL:
```bash
# 1. 删除错误的文件
sudo rm -f /usr/local/bin/docker-compose

# 2. 安装 Docker Compose 插件
sudo yum install docker-compose-plugin -y

# 3. 验证安装
docker compose version
```

**注意**: 新版本命令是 `docker compose`（有空格），不是 `docker-compose`（有横杠）

---

### 方案二：手动下载安装（适合网络好的情况）

```bash
# 1. 删除错误的文件
sudo rm -f /usr/local/bin/docker-compose

# 2. 查看最新版本号
# 访问: https://github.com/docker/compose/releases

# 3. 下载最新版本（替换 v2.24.0 为最新版本）
DOCKER_COMPOSE_VERSION="v2.24.0"
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 4. 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 5. 验证安装
docker-compose --version
```

---

### 方案三：使用国内镜像（GitHub 下载慢时）

```bash
# 1. 删除错误的文件
sudo rm -f /usr/local/bin/docker-compose

# 2. 使用 DaoCloud 镜像源
sudo curl -L https://get.daocloud.io/docker/compose/releases/download/v2.24.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose

# 3. 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 4. 验证安装
docker-compose --version
```

---

### 方案四：安装为 Docker CLI 插件

```bash
# 1. 删除错误的文件
sudo rm -f /usr/local/bin/docker-compose

# 2. 创建插件目录
mkdir -p ~/.docker/cli-plugins/

# 3. 下载 Docker Compose V2
sudo curl -SL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose

# 4. 添加执行权限
sudo chmod +x ~/.docker/cli-plugins/docker-compose

# 5. 验证安装
docker compose version
```

---

## 🔍 验证安装

### 检查 Docker Compose V1（老版本）
```bash
docker-compose --version
# 输出示例: docker-compose version 1.29.2
```

### 检查 Docker Compose V2（新版本）
```bash
docker compose version
# 输出示例: Docker Compose version v2.24.0
```

---

## 🚀 使用修复后的部署脚本

我已经更新了 `deploy.sh` 脚本，现在它可以自动检测你使用的是哪个版本：

```bash
# 重新运行部署脚本
./deploy.sh start
```

脚本会自动检测：
- ✅ 如果安装了 Docker Compose V2，使用 `docker compose`
- ✅ 如果安装了 Docker Compose V1，使用 `docker-compose`
- ❌ 如果都没有，会提示安装

---

## 📝 完整部署流程（修复后）

### 步骤 1: 修复 Docker Compose

选择上面的任一方案安装 Docker Compose

### 步骤 2: 验证安装

```bash
# 验证 Docker
docker --version

# 验证 Docker Compose（任一命令有效即可）
docker compose version
# 或
docker-compose --version
```

### 步骤 3: 配置环境变量

```bash
# 进入项目目录
cd /opt/flask-app

# 复制环境变量模板
cp .env.example .env

# 编辑配置
nano .env
```

**必须修改的配置：**
```bash
DB_PASSWORD=你的强密码
SECRET_KEY=随机生成的密钥
```

生成密钥：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 步骤 4: 修改 docker-compose.yml 密码

```bash
nano docker-compose.yml
```

找到并修改：
```yaml
environment:
  MYSQL_ROOT_PASSWORD: 你的强密码  # 必须与 .env 中的 DB_PASSWORD 一致
  MYSQL_PASSWORD: 你的强密码      # 必须与 .env 中的 DB_PASSWORD 一致
```

### 步骤 5: 启动服务

```bash
# 添加执行权限
chmod +x deploy.sh

# 启动服务
./deploy.sh start
```

### 步骤 6: 检查服务状态

```bash
# 查看状态
./deploy.sh status

# 查看日志
./deploy.sh logs
```

### 步骤 7: 访问应用

浏览器打开: `http://你的服务器IP`

默认账户:
- 用户名: `admin`
- 密码: `admin123`

---

## ⚠️ 常见问题

### Q1: 两个版本有什么区别？

| 特性 | V1 (docker-compose) | V2 (docker compose) |
|------|-------------------|-------------------|
| 命令格式 | `docker-compose` | `docker compose` |
| 安装方式 | 独立二进制文件 | Docker CLI 插件 |
| 性能 | 较慢 | 更快 |
| 推荐使用 | ❌ 已停止维护 | ✅ 官方推荐 |

### Q2: 我应该用哪个版本？

**推荐使用 V2 (docker compose)**：
- 性能更好
- 官方推荐
- 持续更新

但我们的脚本兼容两个版本，所以任一版本都可以。

### Q3: 为什么下载会失败？

可能原因：
1. **网络问题** - GitHub 在国内访问慢
2. **链接失效** - 版本号错误
3. **权限问题** - 需要 sudo 权限

**解决方法**：
- 使用国内镜像源（方案三）
- 使用包管理器安装（方案一）

### Q4: 安装后还是报错？

检查以下几点：

```bash
# 1. 检查文件是否存在
ls -lh /usr/local/bin/docker-compose

# 2. 检查文件类型
file /usr/local/bin/docker-compose
# 应该显示: ELF 64-bit LSB executable

# 3. 如果显示 HTML 或 ASCII text，说明下载失败
cat /usr/local/bin/docker-compose
# 如果看到 HTML 内容，重新下载

# 4. 删除并重新安装
sudo rm /usr/local/bin/docker-compose
# 然后使用方案一重新安装
```

---

## 🔄 完整安装验证脚本

创建一个检查脚本：

```bash
#!/bin/bash

echo "=== Docker 环境检查 ==="

# 检查 Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker 已安装"
    docker --version
else
    echo "❌ Docker 未安装"
fi

echo ""

# 检查 Docker Compose V2
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose V2 已安装"
    docker compose version
else
    echo "❌ Docker Compose V2 未安装"
fi

echo ""

# 检查 Docker Compose V1
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose V1 已安装"
    docker-compose --version
    
    # 检查是否是真实文件
    if file /usr/local/bin/docker-compose | grep -q "ELF"; then
        echo "✅ docker-compose 是有效的可执行文件"
    else
        echo "❌ docker-compose 不是有效的可执行文件（可能是 HTML）"
        echo "请删除并重新安装："
        echo "  sudo rm /usr/local/bin/docker-compose"
    fi
else
    echo "❌ Docker Compose V1 未安装"
fi

echo ""
echo "=== 检查完成 ==="
```

保存为 `check-docker.sh`，运行：

```bash
chmod +x check-docker.sh
./check-docker.sh
```

---

## 📚 相关文档

- [Docker Compose 官方文档](https://docs.docker.com/compose/)
- [Docker Compose 安装指南](https://docs.docker.com/compose/install/)
- [快速部署指南](./QUICK_DEPLOY.md)
- [常见问题解答](./FAQ.md)

---

## 🎯 推荐安装流程（最简单）

如果你不确定选哪个方案，**直接用这个**：

```bash
# 1. 清理旧文件
sudo rm -f /usr/local/bin/docker-compose

# 2. 安装 Docker Compose 插件（最简单）
sudo apt update
sudo apt install docker-compose-plugin -y

# 3. 验证安装
docker compose version

# 4. 运行部署脚本
cd /opt/flask-app
./deploy.sh start
```

**就这么简单！** 🎉

---

## 💡 小贴士

1. **优先使用包管理器安装**（apt/yum）- 最稳定
2. **新项目使用 V2**（`docker compose`）- 官方推荐
3. **老项目可以继续用 V1** - 我们的脚本兼容两者
4. **网络不好时使用国内镜像** - 下载更快

---

需要帮助？查看 [常见问题解答](./FAQ.md) 或提交 Issue。
