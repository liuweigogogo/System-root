# 系统调试指南

## 🚀 初学者调试步骤

### 第一步：环境准备

1. **检查Python版本**
   ```bash
   python --version
   # 确保是Python 3.7+
   ```

2. **检查MySQL服务**
   ```bash
   # Windows
   net start mysql
   
   # 或者通过服务管理器检查MySQL服务是否运行
   ```

3. **安装依赖**
   ```bash
   cd frotend
   pip install -r requirements.txt
   ```

### 第二步：数据库配置

1. **修改数据库配置**
   编辑 `config/DatabaseConfig.py`：
   ```python
   MYSQL_HOST = 'localhost'        # 你的MySQL主机
   MYSQL_USER = 'root'             # 你的MySQL用户名
   MYSQL_PASSWORD = '你的密码'      # 你的MySQL密码
   MYSQL_DB = 'login_system'       # 数据库名称
   ```

2. **测试数据库连接**
   ```bash
   python -c "from config.DatabaseConfig import DatabaseConfig; print('数据库连接测试:', DatabaseConfig.get_connection() is not None)"
   ```

### 第三步：初始化数据库

```bash
python setup_db.py
```

**预期输出：**
```
=== 数据库初始化脚本 ===

检查数据库配置...
主机: localhost
用户: root
数据库: login_system

1. 创建数据库...
数据库 'login_system' 创建成功

2. 创建数据表...
数据表创建成功

3. 创建管理员用户...
管理员用户创建成功
用户名: admin
密码: admin123
请登录后立即修改密码！

=== 初始化完成 ===
现在可以运行 'python app.py' 启动应用
访问 http://localhost:5000 进行登录
```

### 第四步：启动应用

```bash
python app.py
```

**预期输出：**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[::1]:5000
```

### 第五步：测试系统

1. **访问登录页面**
   - 打开浏览器访问 `http://localhost:5000`
   - 应该看到登录界面

2. **测试登录**
   - 用户名：`admin`
   - 密码：`admin123`
   - 输入验证码
   - 点击登录

3. **检查日志**
   - 登录成功后访问 `http://localhost:5000/logs`
   - 查看系统日志

## 🔧 常见问题排查

### 问题1：数据库连接失败

**错误信息：**
```
数据库连接错误: (2003, "Can't connect to MySQL server on 'localhost'")
```

**解决方案：**
1. 检查MySQL服务是否启动
2. 确认数据库配置信息正确
3. 检查防火墙设置

### 问题2：模块导入错误

**错误信息：**
```
ModuleNotFoundError: No module named 'MySQLdb'
```

**解决方案：**
```bash
pip install MySQLdb2
# 或者
pip install PyMySQL
```

### 问题3：端口被占用

**错误信息：**
```
OSError: [Errno 98] Address already in use
```

**解决方案：**
1. 修改 `app.py` 中的端口号：
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)  # 改为5001
   ```
2. 或者关闭占用端口的程序

### 问题4：日志文件权限错误

**解决方案：**
```bash
# 确保logs目录存在且有写权限
mkdir logs
chmod 755 logs
```

## 📊 调试技巧

### 1. 查看实时日志

```bash
# 在另一个终端窗口查看日志
tail -f logs/app.log
tail -f logs/auth.log
tail -f logs/error.log
```

### 2. 测试日志功能

```bash
python log_example.py
```

### 3. 检查数据库表

```sql
-- 连接到MySQL
mysql -u root -p

-- 选择数据库
USE login_system;

-- 查看表结构
SHOW TABLES;
DESCRIBE users;
DESCRIBE user_sessions;

-- 查看用户数据
SELECT * FROM users;
```

### 4. 手动测试API

```bash
# 测试登录API
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","captcha":"TEST"}'

# 测试日志API
curl http://localhost:5000/api/logs
```

## 🎯 逐步完善建议

### 阶段1：基础功能验证
- [ ] 数据库连接正常
- [ ] 用户注册/登录功能
- [ ] 基本日志记录

### 阶段2：安全功能增强
- [ ] 密码强度验证
- [ ] 登录失败锁定
- [ ] 会话超时处理

### 阶段3：企业级功能
- [ ] 用户权限管理
- [ ] 操作审计日志
- [ ] 系统监控面板

### 阶段4：性能优化
- [ ] 数据库连接池
- [ ] 缓存机制
- [ ] 日志压缩

## 🆘 获取帮助

如果遇到问题，请提供：

1. **错误信息**：完整的错误堆栈
2. **环境信息**：Python版本、操作系统
3. **配置信息**：数据库配置（隐藏密码）
4. **日志内容**：相关日志文件内容

这样我可以更准确地帮你解决问题！

