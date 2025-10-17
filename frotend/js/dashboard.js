/**
 * 后台管理系统 - 核心功能模块
 * 包含页面切换、侧边栏控制、用户认证等核心功能
 */

// ===== 全局变量 =====
let selectedFiles = []; // 存储选中的文件
let renamedFiles = [];  // 存储重命名后的文件

/**
 * 页面初始化
 * 在页面加载完成后执行
 */
document.addEventListener('DOMContentLoaded', function() {
    // 检查用户认证状态
    checkAuthStatus();
    
    // 初始化事件监听器
    initializeEventListeners();
});

/**
 * 初始化所有事件监听器
 */
function initializeEventListeners() {
    // 文件重命名工具的事件监听器
    const fileInput = document.getElementById('fileInput');
    const renameRule = document.getElementById('renameRule');
    
    if (fileInput) {
        fileInput.addEventListener('change', updateFileList);
    }
    
    if (renameRule) {
        renameRule.addEventListener('change', updateRuleInput);
    }
    
    // 添加输入框变化时实时预览
    const ruleInput = document.getElementById('ruleInput');
    if (ruleInput) {
        ruleInput.addEventListener('input', previewRename);
    }
}

/**
 * 侧边栏切换功能
 * 在移动端显示/隐藏侧边栏
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

/**
 * 设置导航项为激活状态
 * @param {HTMLElement} link - 被点击的导航链接元素
 */
function setActive(link) {
    // 移除所有导航项的active状态
    const items = document.querySelectorAll('.nav-item');
    items.forEach(function (item) { 
        item.classList.remove('active'); 
    });
    
    // 为当前点击的链接添加active状态
    link.classList.add('active');
}

/**
 * 页面切换功能
 * 在不同页面之间切换显示
 * @param {string} pageId - 页面ID（如'dashboard', 'utilities'）
 */
function showPage(pageId) {
    // 隐藏所有页面
    const pages = document.querySelectorAll('.page-content');
    pages.forEach(page => page.style.display = 'none');
    
    // 显示指定页面
    const targetPage = document.getElementById(pageId + '-page');
    if (targetPage) {
        targetPage.style.display = 'block';
    }
}

/**
 * 切换实用工具折叠菜单
 * 展开或收起实用工具的子菜单
 * @param {HTMLElement} element - 被点击的菜单项元素
 */
function toggleUtilsMenu(element) {
    const submenu = document.getElementById('utils-submenu');
    const toggle = document.getElementById('utils-toggle');
    
    if (!submenu || !toggle) return;
    
    if (submenu.style.display === 'none' || submenu.style.display === '') {
        // 展开菜单
        submenu.style.display = 'block';
        toggle.textContent = '▼';
        toggle.classList.add('expanded');
    } else {
        // 收起菜单
        submenu.style.display = 'none';
        toggle.textContent = '▶';
        toggle.classList.remove('expanded');
    }
}

/**
 * 切换系统设置折叠菜单
 * 展开或收起系统设置的子菜单
 * @param {HTMLElement} element - 被点击的菜单项元素
 */
function toggleSystemMenu(element) {
    const submenu = document.getElementById('system-submenu');
    const toggle = document.getElementById('system-toggle');
    
    if (!submenu || !toggle) return;
    
    if (submenu.style.display === 'none' || submenu.style.display === '') {
        // 展开菜单
        submenu.style.display = 'block';
        toggle.textContent = '▼';
        toggle.classList.add('expanded');
    } else {
        // 收起菜单
        submenu.style.display = 'none';
        toggle.textContent = '▶';
        toggle.classList.remove('expanded');
    }
}

/**
 * 检查用户认证状态
 * 验证用户是否已登录，未登录则跳转到登录页
 */
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/check-auth');
        const data = await response.json();
        
        if (!data.authenticated) {
            // 如果未认证，跳转到登录页面
            window.location.href = '/login';
            return;
        }
        
        // 显示用户信息
        if (data.username) {
            const usernameDisplay = document.getElementById('username-display');
            if (usernameDisplay) {
                usernameDisplay.textContent = data.username;
            }
        }
        
        // 直接使用check-auth返回的用户信息（包括role）
        window.currentUser = {
            id: data.user_id,
            username: data.username,
            role: data.role,
            email: data.email
        };
        
        console.log('当前用户信息:', window.currentUser);
        
        // 根据角色显示/隐藏用户管理菜单
        updateUIBasedOnRole(data.role);
        
    } catch (error) {
        console.error('认证检查失败:', error);
        window.location.href = '/login';
    }
}

/**
 * 根据用户角色更新UI显示
 * @param {string} role - 用户角色 ('admin' 或 'user')
 */
function updateUIBasedOnRole(role) {
    console.log('更新UI根据角色:', role);
    
    // 查找用户管理菜单项（使用更精确的选择器）
    const userManagementMenu = document.querySelector('a.nav-subitem[onclick*="user-management"]');
    
    console.log('找到的用户管理菜单元素:', userManagementMenu);
    
    if (role !== 'admin') {
        // 非管理员：隐藏用户管理菜单项
        console.log('非管理员，隐藏用户管理菜单');
        if (userManagementMenu) {
            userManagementMenu.style.display = 'none';
        }
    } else {
        // 管理员：确保菜单可见
        console.log('管理员身份，显示用户管理菜单');
        if (userManagementMenu) {
            userManagementMenu.style.display = '';
        }
    }
}

/**
 * 用户登出功能
 * 清除会话并跳转到登录页
 */
async function logout() {
    if (confirm('确定要退出登录吗？')) {
        try {
            const response = await fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                window.location.href = '/login';
            } else {
                alert('退出登录失败：' + data.message);
            }
        } catch (error) {
            console.error('退出登录失败:', error);
            alert('退出登录失败，请重试');
        }
    }
}
