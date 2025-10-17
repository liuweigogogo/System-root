# 用户登录系统

一个完整的用户认证系统，包含前端界面、后端API和数据库管理。

## 功能特性

- ✅ 用户登录/注册
- ✅ 验证码验证
- ✅ 密码加密存储
- ✅ 会话管理
- ✅ 安全认证
- ✅ 响应式界面
- ✅ 错误处理
- ✅ 完整日志系统
- ✅ 日志查看和管理
- ✅ 安全事件监控

## 技术栈

### 后端
- **Flask**: Python Web框架
- **MySQL**: 数据库
- **Flask-CORS**: 跨域支持

### 前端
- **HTML5**: 页面结构
- **CSS3**: 样式设计
- **JavaScript**: 交互逻辑

## 安装和运行

### 1. 环境要求

- Python 3.7+
- MySQL 5.7+
- pip (Python包管理器)

### 2. 安装依赖

```bash
# 进入项目目录
cd frotend

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 数据库配置

编辑 `config/DatabaseConfig.py` 文件，修改数据库连接信息：

```python
MYSQL_HOST = 'localhost'        # 数据库主机
MYSQL_USER = 'root'             # 数据库用户名
MYSQL_PASSWORD = '123456'       # 数据库密码
MYSQL_DB = 'login_system'       # 数据库名称
```

### 4. 初始化数据库

```bash
# 运行数据库初始化脚本
python setup_db.py
```

这将创建：
- 数据库和表结构
- 默认管理员账户 (用户名: admin, 密码: admin123)

### 5. 启动应用

```bash
# 启动Flask应用
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 使用说明

### 登录系统

1. 访问 `http://localhost:5000`
2. 输入用户名和密码
3. 输入验证码
4. 点击登录

### 默认账户

- **用户名**: admin
- **密码**: admin123

⚠️ **重要**: 首次登录后请立即修改默认密码！

## 项目结构

```
frotend/
├── app.py                 # Flask应用主文件
├── setup_db.py           # 数据库初始化脚本
├── requirements.txt      # Python依赖
├── README.md            # 项目说明
├── config/
│   └── DatabaseConfig.py # 数据库配置
├── model/
│   └── SqlModel.py      # 数据模型
├── templates/
│   └── dashboard.html   # 仪表板页面
├── css/
│   └── style.css        # 样式文件
├── js/
│   └── script.js        # JavaScript逻辑
├── assets/
│   └── pexels-suzyhazelwood-1629236.jpg # 背景图片
└── index.html           # 登录页面
```

## API接口

### 认证接口

- `POST /api/login` - 用户登录
- `POST /api/register` - 用户注册
- `POST /api/logout` - 用户登出
- `GET /api/check-auth` - 检查认证状态

### 管理接口

- `POST /api/init-db` - 初始化数据库

### 日志接口

- `GET /api/logs` - 获取系统日志
- `POST /api/logs/clear` - 清空日志
- `GET /api/logs/download` - 下载日志
- `GET /logs` - 日志管理页面

## 安全特性

- **密码加密**: 使用PBKDF2算法加密存储
- **会话管理**: 基于令牌的会话系统
- **验证码**: 防止暴力破解
- **输入验证**: 前后端双重验证
- **SQL注入防护**: 使用参数化查询
- **完整日志记录**: 记录所有重要操作和安全事件
- **日志轮转**: 自动管理日志文件大小
- **安全监控**: 实时监控异常登录和安全事件

## 开发说明

### 添加新功能

1. 在 `model/SqlModel.py` 中添加数据模型方法
2. 在 `app.py` 中添加API路由
3. 在前端JavaScript中添加相应的调用逻辑

### 自定义样式

编辑 `css/style.css` 文件来自定义界面样式。

### 数据库扩展

在 `model/SqlModel.py` 中的 `create_tables()` 方法中添加新的表结构。

## 日志系统

### 日志类型

系统提供5种类型的日志文件：

1. **app.log** - 应用主日志
   - 记录应用启动、关闭等基本信息
   - 记录业务逻辑执行情况

2. **auth.log** - 认证相关日志
   - 用户登录/登出记录
   - 认证失败尝试
   - 安全事件记录

3. **database.log** - 数据库操作日志
   - 数据库连接状态
   - SQL操作执行时间
   - 数据库错误记录

4. **error.log** - 错误日志
   - 系统异常和错误
   - 包含完整的错误堆栈信息

5. **access.log** - 访问日志
   - HTTP请求记录
   - 用户访问行为
   - IP地址和用户代理信息

### 日志特性

- **自动轮转**: 单个日志文件最大10MB，保留5个备份文件
- **分级记录**: 支持INFO、WARNING、ERROR等不同级别
- **实时监控**: 可通过Web界面实时查看日志
- **安全记录**: 自动记录所有安全相关事件
- **性能监控**: 记录数据库操作执行时间

### 日志查看

1. **Web界面查看**:
   - 登录系统后访问 `/logs` 页面
   - 支持按类型、级别筛选日志
   - 可设置显示行数

2. **文件直接查看**:
   - 日志文件位于 `logs/` 目录
   - 可使用文本编辑器或命令行工具查看

3. **下载日志**:
   - 支持下载指定类型的日志文件
   - 便于离线分析和备份

### 日志管理

- **清空日志**: 可通过Web界面清空所有日志文件
- **日志下载**: 支持按类型下载日志文件
- **自动清理**: 系统会自动管理日志文件大小

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 验证数据库配置信息
   - 确认数据库用户权限

2. **依赖安装失败**
   - 使用 `pip install --upgrade pip` 升级pip
   - 尝试使用虚拟环境

3. **端口占用**
   - 修改 `app.py` 中的端口号
   - 检查5000端口是否被其他程序占用

### 日志查看

应用运行时会在控制台输出详细的日志信息，包括：
- 数据库连接状态
- API请求日志
- 错误信息

## 许可证

本项目仅供学习和开发使用。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。
