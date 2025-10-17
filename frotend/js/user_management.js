/**
 * 用户管理前端交互脚本
 * 提供用户CRUD操作的前端逻辑和API调用
 */

// 全局变量
let currentPage = 1;
const pageSize = 10;
let currentSearch = '';
let currentRoleFilter = '';

/**
 * 初始化用户管理模块
 * 在页面加载完成后调用
 */
function initUserManagement() {
    console.log('初始化用户管理模块');
    
    // 检查当前用户角色
    const currentUser = window.currentUser;
    const isAdmin = currentUser && currentUser.role === 'admin';
    
    if (isAdmin) {
        // 管理员：加载所有用户
        loadUsers();
        loadStatistics();
    } else {
        // 普通用户：只显示自己的信息
        loadCurrentUserOnly();
        hideAdminFeatures();
    }
    
    // 绑定搜索事件（仅管理员）
    if (isAdmin) {
        const searchInput = document.getElementById('userSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(function() {
                currentSearch = this.value;
                currentPage = 1;
                loadUsers();
            }, 500));
        }
        
        // 绑定角色过滤事件
        const roleFilter = document.getElementById('roleFilter');
        if (roleFilter) {
            roleFilter.addEventListener('change', function() {
                currentRoleFilter = this.value;
                currentPage = 1;
                loadUsers();
            });
        }
    }
}

/**
 * 加载用户列表
 * 从后端API获取用户数据并渲染到表格
 */
async function loadUsers() {
    try {
        // 构建查询参数
        const params = new URLSearchParams({
            page: currentPage,
            page_size: pageSize
        });
        
        if (currentSearch) {
            params.append('search', currentSearch);
        }
        
        if (currentRoleFilter) {
            params.append('role', currentRoleFilter);
        }
        
        // 调用API
        const response = await fetch(`/api/users?${params.toString()}`, {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.status === 403) {
            alert('权限不足，仅限管理员访问');
            return;
        }
        
        if (!data.success) {
            console.error('获取用户列表失败:', data.message);
            showError('获取用户列表失败: ' + data.message);
            return;
        }
        
        // 渲染用户列表
        renderUserTable(data.data.users);
        
        // 渲染分页
        renderPagination(data.data.pagination);
        
    } catch (error) {
        console.error('加载用户列表失败:', error);
        showError('加载用户列表失败');
    }
}

/**
 * 加载统计信息
 * 从后端API获取用户统计数据
 */
async function loadStatistics() {
    try {
        const response = await fetch('/api/users/statistics', {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateStatistics(data.data);
        }
    } catch (error) {
        console.error('加载统计信息失败:', error);
    }
}

/**
 * 加载当前用户信息（仅普通用户）
 * 普通用户只能查看自己的信息
 */
async function loadCurrentUserOnly() {
    const currentUser = window.currentUser;
    if (!currentUser) {
        showError('无法获取当前用户信息');
        return;
    }
    
    // 渲染单个用户信息
    renderUserTable([currentUser]);
    
    // 隐藏分页
    const paginationContainer = document.getElementById('paginationContainer');
    if (paginationContainer) {
        paginationContainer.style.display = 'none';
    }
    
    // 更新统计信息（只显示1个用户）
    updateStatistics({
        total_users: 1,
        admin_count: currentUser.role === 'admin' ? 1 : 0,
        active_users: currentUser.is_active ? 1 : 0,
        new_this_month: 0,
        online_users: 1
    });
}

/**
 * 隐藏管理员功能（普通用户）
 * 隐藏添加、搜索、过滤等功能
 */
function hideAdminFeatures() {
    // 隐藏添加用户按钮
    const addButton = document.querySelector('button[onclick="openUserModal(\'add\')"]');
    if (addButton) {
        addButton.style.display = 'none';
    }
    
    // 隐藏搜索框
    const searchInput = document.getElementById('userSearchInput');
    if (searchInput) {
        searchInput.parentElement.style.display = 'none';
    }
    
    // 显示提示信息
    const toolbar = document.querySelector('.tool-body > div:nth-child(2)');
    if (toolbar) {
        const notice = document.createElement('div');
        notice.style.cssText = 'background: #fef3c7; color: #92400e; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #f59e0b;';
        notice.innerHTML = '⚠️ 你是普通用户，只能查看自己的信息，无法管理其他用户。';
        toolbar.parentElement.insertBefore(notice, toolbar);
    }
}

/**
 * 渲染用户表格
 * @param {Array} users - 用户列表数组
 */
function renderUserTable(users) {
    const tbody = document.getElementById('userTableBody');
    if (!tbody) return;
    
    if (users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 40px; color: #999;">
                    暂无用户数据
                </td>
            </tr>
        `;
        return;
    }
    
    // 检查当前用户是否为管理员
    const currentUser = window.currentUser;
    const isAdmin = currentUser && currentUser.role === 'admin';
    
    tbody.innerHTML = users.map(user => `
        <tr style="border-bottom: 1px solid #f3f4f6; transition: background 0.2s;" 
            onmouseover="this.style.background='#f9fafb'" 
            onmouseout="this.style.background='white'">
            <td style="padding: 15px;">#${user.id}</td>
            <td style="padding: 15px; font-weight: 500;">
                ${user.role === 'admin' ? '👑' : '👤'} ${user.username}
            </td>
            <td style="padding: 15px;">${user.email || '-'}</td>
            <td style="padding: 15px;">
                <span style="background: ${user.role === 'admin' ? '#fef3c7' : '#dbeafe'}; 
                             color: ${user.role === 'admin' ? '#92400e' : '#1e40af'}; 
                             padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                    ${user.role === 'admin' ? '管理员' : '普通用户'}
                </span>
            </td>
            <td style="padding: 15px;">
                <span style="background: ${user.is_active ? '#dcfce7' : '#fee2e2'}; 
                             color: ${user.is_active ? '#166534' : '#991b1b'}; 
                             padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                    ${user.is_active ? '✅ 正常' : '🚫 禁用'}
                </span>
            </td>
            <td style="padding: 15px; color: #64748b;">
                ${formatDate(user.created_at)}
            </td>
            <td style="padding: 15px; text-align: center;">
                ${isAdmin ? `
                    <button onclick="editUser(${user.id})" 
                            style="padding: 6px 12px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; margin-right: 5px; font-size: 12px;">
                        ✏️ 编辑
                    </button>
                    <button onclick="deleteUser(${user.id}, '${user.username}')" 
                            style="padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px;">
                        🗑️ 删除
                    </button>
                ` : `
                    <span style="color: #9ca3af; font-size: 12px;">无权限</span>
                `}
            </td>
        </tr>
    `).join('');
}

/**
 * 更新统计信息卡片
 * @param {Object} stats - 统计数据对象
 */
function updateStatistics(stats) {
    // 更新各个统计卡片的数字
    const statCards = document.querySelectorAll('.stat-card div:last-child');
    if (statCards.length >= 4) {
        statCards[0].textContent = stats.total_users || 0;
        statCards[1].textContent = stats.admin_count || 0;
        statCards[2].textContent = stats.online_users || 0;
        statCards[3].textContent = stats.new_this_month || 0;
    }
}

/**
 * 渲染分页组件
 * @param {Object} pagination - 分页信息对象
 */
function renderPagination(pagination) {
    const container = document.getElementById('paginationContainer');
    if (!container) return;
    
    const { page, page_size, total, total_pages } = pagination;
    
    let html = `
        <div style="color: #64748b; font-size: 14px;">
            显示 ${(page - 1) * page_size + 1}-${Math.min(page * page_size, total)} 条，共 ${total} 条
        </div>
        <div style="display: flex; gap: 5px;">
    `;
    
    // 上一页按钮
    html += `
        <button onclick="changePage(${page - 1})" 
                ${page <= 1 ? 'disabled' : ''}
                style="padding: 8px 12px; border: 1px solid #d1d5db; background: white; border-radius: 6px; cursor: pointer; font-size: 14px;">
            ⬅️ 上一页
        </button>
    `;
    
    // 页码按钮
    for (let i = Math.max(1, page - 2); i <= Math.min(total_pages, page + 2); i++) {
        html += `
            <button onclick="changePage(${i})" 
                    style="padding: 8px 12px; 
                           border: 1px solid ${i === page ? '#4f46e5' : '#d1d5db'}; 
                           background: ${i === page ? '#4f46e5' : 'white'}; 
                           color: ${i === page ? 'white' : 'black'}; 
                           border-radius: 6px; 
                           cursor: pointer; 
                           font-size: 14px;
                           ${i === page ? 'font-weight: 600;' : ''}">
                ${i}
            </button>
        `;
    }
    
    // 下一页按钮
    html += `
        <button onclick="changePage(${page + 1})" 
                ${page >= total_pages ? 'disabled' : ''}
                style="padding: 8px 12px; border: 1px solid #d1d5db; background: white; border-radius: 6px; cursor: pointer; font-size: 14px;">
            ➡️ 下一页
        </button>
    `;
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * 切换页码
 * @param {number} page - 目标页码
 */
function changePage(page) {
    currentPage = page;
    loadUsers();
}

/**
 * 打开用户模态框（添加/编辑）
 * @param {string} mode - 模式 ('add' 或 'edit')
 * @param {number} userId - 用户ID（编辑模式时使用）
 */
async function openUserModal(mode, userId = null) {
    const modal = document.getElementById('userModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('userForm');
    
    modal.style.display = 'flex';
    
    if (mode === 'add') {
        modalTitle.textContent = '➕ 添加用户';
        form.reset();
        form.dataset.mode = 'add';
        form.dataset.userId = '';
    } else if (mode === 'edit' && userId) {
        modalTitle.textContent = '✏️ 编辑用户';
        form.dataset.mode = 'edit';
        form.dataset.userId = userId;
        
        // 加载用户数据
        try {
            const response = await fetch(`/api/users/${userId}`, {
                credentials: 'include'
            });
            const data = await response.json();
            
            if (data.success) {
                const user = data.data;
                document.getElementById('username').value = user.username;
                document.getElementById('email').value = user.email || '';
                document.getElementById('role').value = user.role;
                document.getElementById('status').value = user.is_active ? 'active' : 'inactive';
                // 密码字段留空（编辑时可选）
                document.getElementById('password').value = '';
            }
        } catch (error) {
            console.error('加载用户数据失败:', error);
            alert('加载用户数据失败');
        }
    }
}

/**
 * 关闭用户模态框
 */
function closeUserModal() {
    document.getElementById('userModal').style.display = 'none';
}

/**
 * 提交用户表单（创建或更新）
 * @param {Event} event - 表单提交事件
 */
async function submitUserForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const mode = form.dataset.mode;
    const userId = form.dataset.userId;
    
    // 收集表单数据
    const formData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        role: document.getElementById('role').value,
        is_active: document.getElementById('status').value === 'active'
    };
    
    const password = document.getElementById('password').value;
    if (password) {
        formData.password = password;
    } else if (mode === 'add') {
        alert('创建用户时必须提供密码');
        return;
    }
    
    try {
        let response;
        
        if (mode === 'add') {
            // 创建用户
            response = await fetch('/api/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(formData)
            });
        } else {
            // 更新用户
            response = await fetch(`/api/users/${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(formData)
            });
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert(mode === 'add' ? '用户创建成功！' : '用户更新成功！');
            closeUserModal();
            loadUsers();
            loadStatistics();
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('提交表单失败:', error);
        alert('操作失败，请重试');
    }
}

/**
 * 编辑用户
 * @param {number} userId - 用户ID
 */
function editUser(userId) {
    openUserModal('edit', userId);
}

/**
 * 删除用户
 * @param {number} userId - 用户ID
 * @param {string} username - 用户名
 */
async function deleteUser(userId, username) {
    if (!confirm(`确定要删除用户 "${username}" 吗？此操作不可恢复！`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('用户删除成功！');
            loadUsers();
            loadStatistics();
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('删除用户失败:', error);
        alert('删除失败，请重试');
    }
}

/**
 * 格式化日期
 * @param {string} dateString - 日期字符串
 * @returns {string} - 格式化后的日期
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} - 防抖后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 显示错误消息
 * @param {string} message - 错误消息
 */
function showError(message) {
    alert(message);
}

// 当标签页内容加载完成时自动初始化
// 注意：这个会在tab内容被渲染后由TabManager调用
window.initUserManagement = initUserManagement;
