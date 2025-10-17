# 用户管理 API 文档

## 📋 概述

用户管理系统提供完整的CRUD操作，**仅限管理员权限访问**。实现了一级权限隔离，普通用户无法访问用户管理功能。

---

## 🔒 权限说明

### 角色类型
- `user`: 普通用户
- `admin`: 管理员

### 权限控制
- ✅ **管理员** (`role='admin'`): 可以访问所有用户管理接口
- ❌ **普通用户** (`role='user'`): 无法访问用户管理接口，返回403错误

### 权限验证流程
1. 检查用户是否登录（验证session_token）
2. 验证用户身份和会话有效性
3. 检查用户角色是否为admin
4. 通过验证后才能访问接口

---

## 🚀 安装和配置

### 1. 运行数据库迁移（添加role字段）

如果你的数据库已存在，需要运行迁移脚本：

```bash
# 进入项目目录
cd "d:\Program Files\JetBrains\PythonProject\project-root\frotend"

# 运行迁移脚本
python migrate_add_user_role.py
```

### 2. 或者重新初始化数据库

如果是全新安装，可以重新初始化：

```bash
python setup_db.py
```

### 3. 启动应用

```bash
python app.py
```

---

## 📡 API 接口列表

Base URL: `http://127.0.0.1:5000/api/users`

所有接口都需要管理员权限，请求需要包含有效的session token（通过登录获得）。

### 1. 获取用户列表（分页、搜索、过滤）

**Endpoint:** `GET /api/users`

**权限:** 🔒 仅管理员

**Query Parameters:**
- `page` (int, optional): 页码，默认1
- `page_size` (int, optional): 每页数量，默认10，最大100
- `search` (string, optional): 搜索关键词（匹配用户名或邮箱）
- `role` (string, optional): 角色过滤 (`admin` 或 `user`)

**Request Example:**
```bash
GET /api/users?page=1&page_size=10&search=zhang&role=user
```

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "zhangsan",
        "email": "zhangsan@example.com",
        "role": "user",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00",
        "last_login": "2024-10-16T14:20:00"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total": 125,
      "total_pages": 13
    }
  }
}
```

**Response Error (403):**
```json
{
  "success": false,
  "message": "权限不足，仅限管理员访问",
  "error_code": "PERMISSION_DENIED"
}
```

---

### 2. 获取单个用户详情

**Endpoint:** `GET /api/users/{user_id}`

**权限:** 🔒 仅管理员

**Path Parameters:**
- `user_id` (int): 用户ID

**Request Example:**
```bash
GET /api/users/1001
```

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "id": 1001,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "last_login": "2024-10-16T15:30:00"
  }
}
```

**Response Error (404):**
```json
{
  "success": false,
  "message": "用户不存在"
}
```

---

### 3. 创建新用户

**Endpoint:** `POST /api/users`

**权限:** 🔒 仅管理员

**Request Body:**
```json
{
  "username": "newuser",
  "password": "securePassword123",
  "email": "newuser@example.com",
  "role": "user"
}
```

**Required Fields:**
- `username` (string): 用户名，必须唯一
- `password` (string): 密码

**Optional Fields:**
- `email` (string): 邮箱地址
- `role` (string): 用户角色，`user` 或 `admin`，默认为 `user`

**Response Success (201):**
```json
{
  "success": true,
  "message": "用户创建成功",
  "data": {
    "user_id": 1005
  }
}
```

**Response Error (400):**
```json
{
  "success": false,
  "message": "用户名已存在"
}
```

---

### 4. 更新用户信息

**Endpoint:** `PUT /api/users/{user_id}`

**权限:** 🔒 仅管理员

**Path Parameters:**
- `user_id` (int): 用户ID

**Request Body (所有字段可选):**
```json
{
  "username": "updated_username",
  "email": "updated@example.com",
  "password": "newPassword123",
  "role": "admin",
  "is_active": false
}
```

**Optional Fields:**
- `username` (string): 新用户名
- `email` (string): 新邮箱
- `password` (string): 新密码（会自动加密）
- `role` (string): 新角色 (`user` 或 `admin`)
- `is_active` (boolean): 账户状态

**Response Success (200):**
```json
{
  "success": true,
  "message": "用户信息更新成功"
}
```

**Response Error (400):**
```json
{
  "success": false,
  "message": "用户名已被使用"
}
```

---

### 5. 删除用户

**Endpoint:** `DELETE /api/users/{user_id}`

**权限:** 🔒 仅管理员

**Path Parameters:**
- `user_id` (int): 用户ID

**限制:**
- ❌ 不能删除自己的账户
- ❌ 不能删除最后一个管理员账户

**Request Example:**
```bash
DELETE /api/users/1003
```

**Response Success (200):**
```json
{
  "success": true,
  "message": "用户删除成功"
}
```

**Response Error (400):**
```json
{
  "success": false,
  "message": "不能删除最后一个管理员账户"
}
```

---

### 6. 获取用户统计信息

**Endpoint:** `GET /api/users/statistics`

**权限:** 🔒 仅管理员

**Request Example:**
```bash
GET /api/users/statistics
```

**Response Success (200):**
```json
{
  "success": true,
  "data": {
    "total_users": 125,
    "admin_count": 8,
    "active_users": 120,
    "new_this_month": 18,
    "online_users": 42
  }
}
```

**字段说明:**
- `total_users`: 总用户数
- `admin_count`: 管理员数量
- `active_users`: 活跃用户数（is_active=true）
- `new_this_month`: 本月新增用户数
- `online_users`: 当前在线用户数（有效会话）

---

## 🔐 错误代码

| 错误代码 | HTTP状态码 | 说明 |
|---------|----------|------|
| `NOT_AUTHENTICATED` | 401 | 未登录 |
| `SESSION_EXPIRED` | 401 | 会话已过期 |
| `USER_NOT_FOUND` | 404 | 用户不存在 |
| `PERMISSION_DENIED` | 403 | 权限不足（非管理员） |

---

## 📁 文件结构

```
frotend/
├── model/
│   └── BaseUser.py                    # 用户模型（已添加role字段）
├── services/
│   ├── UserManagementService.py       # 用户管理服务（CRUD逻辑）
│   └── PermissionService.py           # 权限装饰器
├── controllers/
│   └── UserManagementController.py    # 用户管理控制器（API接口）
├── config/
│   └── DatabaseSchema.py              # 数据库表结构（已添加role字段）
├── migrate_add_user_role.py           # 数据库迁移脚本
└── app.py                             # 主应用（已注册用户管理蓝图）
```

---

## 🛠️ 前端集成

前端已经实现完整的用户管理界面，包括：

- ✅ 用户列表展示（表格）
- ✅ 分页功能
- ✅ 搜索和过滤
- ✅ 添加用户表单（模态框）
- ✅ 编辑用户表单（模态框）
- ✅ 删除用户（确认提示）
- ✅ 用户统计卡片

### 前端调用示例

```javascript
// 获取用户列表
async function fetchUsers(page = 1, search = '', role = '') {
  const response = await fetch(
    `/api/users?page=${page}&page_size=10&search=${search}&role=${role}`,
    {
      method: 'GET',
      credentials: 'include' // 包含session cookie
    }
  );
  
  if (response.status === 403) {
    alert('权限不足，仅限管理员访问');
    return;
  }
  
  const data = await response.json();
  if (data.success) {
    // 处理用户列表
    displayUsers(data.data.users);
    displayPagination(data.data.pagination);
  }
}

// 创建用户
async function createUser(userData) {
  const response = await fetch('/api/users', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify(userData)
  });
  
  const data = await response.json();
  if (data.success) {
    alert('用户创建成功！');
    fetchUsers(); // 刷新列表
  } else {
    alert(data.message);
  }
}

// 更新用户
async function updateUser(userId, updates) {
  const response = await fetch(`/api/users/${userId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    credentials: 'include',
    body: JSON.stringify(updates)
  });
  
  const data = await response.json();
  if (data.success) {
    alert('用户更新成功！');
    fetchUsers(); // 刷新列表
  }
}

// 删除用户
async function deleteUser(userId) {
  if (!confirm('确定要删除该用户吗？')) return;
  
  const response = await fetch(`/api/users/${userId}`, {
    method: 'DELETE',
    credentials: 'include'
  });
  
  const data = await response.json();
  if (data.success) {
    alert('用户删除成功！');
    fetchUsers(); // 刷新列表
  } else {
    alert(data.message);
  }
}
```

---

## 🧪 测试

### 使用curl测试

```bash
# 1. 先登录获取session
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c cookies.txt

# 2. 获取用户列表
curl -X GET http://127.0.0.1:5000/api/users?page=1&page_size=10 \
  -b cookies.txt

# 3. 创建新用户
curl -X POST http://127.0.0.1:5000/api/users \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"username":"testuser","password":"test123","email":"test@example.com","role":"user"}'

# 4. 更新用户
curl -X PUT http://127.0.0.1:5000/api/users/1002 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"email":"newemail@example.com","is_active":false}'

# 5. 删除用户
curl -X DELETE http://127.0.0.1:5000/api/users/1003 \
  -b cookies.txt

# 6. 获取统计信息
curl -X GET http://127.0.0.1:5000/api/users/statistics \
  -b cookies.txt
```

---

## 📝 注意事项

1. **权限隔离**: 所有用户管理接口都有 `@admin_required` 装饰器保护
2. **密码加密**: 密码使用bcrypt加密存储，不会以明文保存
3. **会话验证**: 每次请求都会验证session有效性
4. **级联删除**: 删除用户时会自动删除相关会话
5. **最后管理员保护**: 不允许删除最后一个管理员账户
6. **自我保护**: 管理员不能删除自己的账户

---

## 🎯 下一步

后端API已经完全实现，现在可以：

1. **测试API**: 使用Postman或curl测试所有接口
2. **前端集成**: 将前端的用户管理界面与这些API对接
3. **权限管理**: 在前端检查用户角色，隐藏非管理员的用户管理菜单

---

## 📞 支持

如有问题，请查看日志文件：
- `logs/app.log` - 应用日志
- `logs/auth.log` - 认证日志
- `logs/security.log` - 安全日志
