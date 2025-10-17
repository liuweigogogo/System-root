/**
 * 页签管理系统
 * 实现类似浏览器标签页的多页签功能
 * 支持打开、切换、关闭页签
 */

// 页签管理器对象
const TabManager = {
    // 存储所有已打开的页签
    tabs: [],
    // 当前活动的页签ID
    activeTabId: null,
    // 页签ID计数器
    tabIdCounter: 0,
    
    /**
     * 初始化页签管理器
     * 在页面加载时调用
     */
    init() {
        console.log('页签管理器已初始化');
    },
    
    /**
     * 获取工具所属的页面类型（utilities 或 system-settings）
     * @param {string} toolId - 工具ID
     * @returns {string} - 页面类型
     */
    getPageType(toolId) {
        // 定义工具与页面的映射关系
        const toolPageMap = {
            'file-converter': 'utilities',
            'user-management': 'system-settings',
            'system-logs': 'system-settings'
        };
        return toolPageMap[toolId] || 'utilities';
    },
    
    /**
     * 获取页面对应的DOM元素ID
     * @param {string} pageType - 页面类型
     * @returns {object} - 包含container, list, content, placeholder的对象
     */
    getPageElements(pageType) {
        if (pageType === 'system-settings') {
            return {
                container: 'systemTabsContainer',
                list: 'systemTabsList',
                content: 'systemTabsContent',
                placeholder: 'systemNoTabsPlaceholder'
            };
        }
        // 默认返回utilities页面的元素
        return {
            container: 'tabsContainer',
            list: 'tabsList',
            content: 'tabsContent',
            placeholder: 'noTabsPlaceholder'
        };
    },
    
    /**
     * 打开新页签
     * @param {string} toolId - 工具唯一标识符（如'file-converter'）
     * @param {string} title - 页签标题（如'🔄 文件格式转换'）
     */
    openTab(toolId, title) {
        console.log('打开页签:', toolId, title);
        
        // 获取工具所属的页面类型
        const pageType = this.getPageType(toolId);
        const elements = this.getPageElements(pageType);
        
        // 检查是否已经打开了该工具的页签
        const existingTab = this.tabs.find(tab => tab.toolId === toolId);
        if (existingTab) {
            // 如果已存在，则切换到该页签
            console.log('页签已存在，切换到:', existingTab.id);
            this.switchTab(existingTab.id, pageType);
            return;
        }
        
        // 创建新页签ID
        const tabId = `tab-${this.tabIdCounter++}`;
        
        // 获取工具内容模板
        const contentHtml = this.getToolContent(toolId);
        
        // 创建页签对象
        const tab = {
            id: tabId,
            toolId: toolId,
            title: title,
            pageType: pageType
        };
        
        // 添加到页签列表
        this.tabs.push(tab);
        
        // 渲染页签到DOM
        this.renderTab(tab, elements.list);
        
        // 渲染页签内容到DOM
        this.renderTabContent(tab, contentHtml, elements.content);
        
        // 切换到新页签
        this.switchTab(tabId, pageType);
        
        // 显示页签容器
        this.showTabsContainer(pageType);
    },
    
    /**
     * 切换到指定页签
     * @param {string} tabId - 页签ID
     * @param {string} pageType - 页面类型
     */
    switchTab(tabId, pageType) {
        const elements = this.getPageElements(pageType);
        const container = document.getElementById(elements.container);
        
        if (!container) return;
        
        // 移除该容器内所有页签和内容的active状态
        container.querySelectorAll('.tab-item').forEach(item => {
            item.classList.remove('active');
        });
        container.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // 激活指定页签和内容
        const tabElement = container.querySelector(`[data-tab-id="${tabId}"]`);
        const contentElement = container.querySelector(`#content-${tabId}`);
        
        if (tabElement) tabElement.classList.add('active');
        if (contentElement) contentElement.classList.add('active');
        
        // 更新活动页签ID
        this.activeTabId = tabId;
    },
    
    /**
     * 关闭指定页签
     * @param {string} tabId - 页签ID
     */
    closeTab(tabId) {
        // 从页签列表中移除
        const tabIndex = this.tabs.findIndex(tab => tab.id === tabId);
        if (tabIndex === -1) return;
        
        const tab = this.tabs[tabIndex];
        const pageType = tab.pageType;
        const elements = this.getPageElements(pageType);
        
        this.tabs.splice(tabIndex, 1);
        
        // 从DOM中移除页签和内容
        const container = document.getElementById(elements.container);
        if (container) {
            const tabElement = container.querySelector(`[data-tab-id="${tabId}"]`);
            const contentElement = container.querySelector(`#content-${tabId}`);
            
            if (tabElement) tabElement.remove();
            if (contentElement) contentElement.remove();
        }
        
        // 如果关闭的是当前活动页签，切换到其他页签
        const remainingTabsInPage = this.tabs.filter(t => t.pageType === pageType);
        if (this.activeTabId === tabId && remainingTabsInPage.length > 0) {
            // 切换到前一个页签或下一个页签
            const newActiveTab = remainingTabsInPage[Math.max(0, Math.min(tabIndex, remainingTabsInPage.length - 1))];
            this.switchTab(newActiveTab.id, pageType);
        }
        
        // 如果该页面没有页签了，隐藏页签容器
        if (remainingTabsInPage.length === 0) {
            this.hideTabsContainer(pageType);
        }
    },
    
    /**
     * 渲染页签到DOM
     * @param {object} tab - 页签对象
     * @param {string} listElementId - 页签列表元素ID
     */
    renderTab(tab, listElementId) {
        const tabsList = document.getElementById(listElementId);
        if (!tabsList) return;
        
        const tabItem = document.createElement('div');
        tabItem.className = 'tab-item';
        tabItem.setAttribute('data-tab-id', tab.id);
        tabItem.innerHTML = `
            <span class="tab-title" onclick="TabManager.switchTab('${tab.id}', '${tab.pageType}')">${tab.title}</span>
            <span class="tab-close" onclick="TabManager.closeTab('${tab.id}'); event.stopPropagation();">×</span>
        `;
        
        tabsList.appendChild(tabItem);
    },
    
    /**
     * 渲染页签内容到DOM
     * @param {object} tab - 页签对象
     * @param {string} contentHtml - 内容HTML
     * @param {string} contentElementId - 内容容器元素ID
     */
    renderTabContent(tab, contentHtml, contentElementId) {
        const tabsContent = document.getElementById(contentElementId);
        if (!tabsContent) return;
        
        const tabPane = document.createElement('div');
        tabPane.className = 'tab-pane';
        tabPane.id = `content-${tab.id}`;
        tabPane.innerHTML = contentHtml;
        
        tabsContent.appendChild(tabPane);
        
        // 如果是文件转换器，重新初始化
        if (tab.toolId === 'file-converter') {
            console.log('初始化文件转换器...');
            // 等待DOM插入后初始化
            setTimeout(() => {
                if (window.fileConverter) {
                    window.fileConverter.init();
                } else if (typeof IntegratedFileConverter !== 'undefined') {
                    window.fileConverter = new IntegratedFileConverter();
                }
            }, 100);
        }
        
        // 如果是用户管理，初始化用户管理模块
        if (tab.toolId === 'user-management') {
            console.log('初始化用户管理模块...');
            // 等待DOM插入后初始化
            setTimeout(() => {
                if (typeof initUserManagement === 'function') {
                    initUserManagement();
                } else {
                    console.error('initUserManagement 函数未定义，请确保 user_management.js 已加载');
                }
            }, 100);
        }
    },
    
    /**
     * 获取工具内容HTML模板
     * @param {string} toolId - 工具ID
     * @returns {string} - 工具内容HTML
     */
    getToolContent(toolId) {
        // 文件转换器的内容模板
        if (toolId === 'file-converter') {
            return `
                <div class="tool-header">
                    <h3>🔄 文件格式转换</h3>
                    <p>支持Word、Excel、PowerPoint、PDF、图片等多种格式相互转换</p>
                </div>
                <div class="tool-body" style="padding: 20px;">
                    <!-- 支持的转换格式说明 -->
                    <div class="converter-section">
                        <h4>🎯 支持的转换类型</h4>
                        <div class="format-support-grid">
                            <div class="format-card">
                                <div class="format-icon">📄</div>
                                <div class="format-title">文档转换</div>
                                <div class="format-items">DOCX ⇄ PDF</div>
                            </div>
                            <div class="format-card">
                                <div class="format-icon">📊</div>
                                <div class="format-title">表格转换</div>
                                <div class="format-items">XLSX ⇄ CSV ⇄ JSON</div>
                            </div>
                            <div class="format-card">
                                <div class="format-icon">📰</div>
                                <div class="format-title">演示转换</div>
                                <div class="format-items">PPTX → PDF</div>
                            </div>
                            <div class="format-card">
                                <div class="format-icon">🖼️</div>
                                <div class="format-title">图片转换</div>
                                <div class="format-items">JPG ⇄ PNG ⇄ WEBP</div>
                            </div>
                        </div>
                    </div>

                    <!-- 文件转换表单 -->
                    <div class="converter-section">
                        <h4>📎 开始转换</h4>
                        <form id="fileConvertForm" enctype="multipart/form-data" style="margin-top: 15px;">
                            <div class="form-row">
                                <div class="form-group" style="flex: 2;">
                                    <label for="converterFileInput">📂 选择文件：</label>
                                    <input type="file" id="converterFileInput" name="file" 
                                           accept=".docx,.doc,.xlsx,.xls,.pptx,.ppt,.pdf,.csv,.json,.jpg,.jpeg,.png,.webp,.gif,.bmp"
                                           required style="width: 100%; padding: 10px; border: 2px dashed #ccc; border-radius: 5px; cursor: pointer;">
                                    <small style="color: #666; display: block; margin-top: 5px;">支持：.docx, .xlsx, .pptx, .pdf, .csv, .json, .jpg, .png 等</small>
                                </div>
                                <div class="form-group" style="flex: 1;">
                                    <label for="targetFormat">🎯 目标格式：</label>
                                    <select id="targetFormat" name="target_format" required 
                                            style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                                        <option value="">请先选择文件</option>
                                    </select>
                                </div>
                                <div class="form-group" style="flex: 0 0 auto; align-self: flex-end;">
                                    <button type="submit" class="btn-convert" style="padding: 10px 30px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: 600;">
                                        <span class="btn-text">⚙️ 开始转换</span>
                                        <span class="btn-loading" style="display: none;">⏳ 转换中...</span>
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>

                    <!-- 转换结果区域 -->
                    <div id="conversionResult" class="converter-section" style="display: none;">
                        <h4>✅ 转换结果</h4>
                        <div id="resultContent" class="result-content">
                            <!-- 动态填充结果内容 -->
                        </div>
                    </div>

                    <!-- 错误信息区域 -->
                    <div id="conversionError" class="converter-section" style="display: none;">
                        <h4 style="color: #ef4444;">❌ 转换失败</h4>
                        <div id="errorContent" class="error-content" style="background: #fee; padding: 15px; border-radius: 5px; border-left: 4px solid #ef4444;">
                            <!-- 动态填充错误内容 -->
                        </div>
                    </div>

                    <!-- 转换历史 -->
                    <div class="converter-section">
                        <h4>📋 转换历史</h4>
                        <div id="conversionHistory" class="conversion-history">
                            <p style="text-align: center; color: #999; padding: 20px;">暂无转换记录</p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // 用户管理的内容模板
        if (toolId === 'user-management') {
            return `
                <div class="tool-header">
                    <h3>👥 用户管理</h3>
                    <p>用户信息的增删改查操作（仅管理员权限）</p>
                </div>
                <div class="tool-body" style="padding: 20px;">
                    <!-- 用户统计卡片 -->
                    <div class="user-stats" style="margin-bottom: 30px;">
                        <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                            <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">👥 总用户数</div>
                                <div style="font-size: 32px; font-weight: bold;">125</div>
                            </div>
                            <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);">
                                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">👑 管理员</div>
                                <div style="font-size: 32px; font-weight: bold;">8</div>
                            </div>
                            <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);">
                                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">🟢 在线用户</div>
                                <div style="font-size: 32px; font-weight: bold;">42</div>
                            </div>
                            <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 20px; border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(67, 233, 123, 0.3);">
                                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">✨ 本月新增</div>
                                <div style="font-size: 32px; font-weight: bold;">18</div>
                            </div>
                        </div>
                    </div>

                    <!-- 操作栏 -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <div style="display: flex; gap: 10px;">
                            <input type="text" id="userSearchInput" placeholder="🔍 搜索用户名、邮箱..." 
                                   style="padding: 10px 15px; border: 1px solid #d1d5db; border-radius: 8px; width: 300px; font-size: 14px;">
                            <select id="roleFilter" style="padding: 10px 15px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px;">
                                <option value="">所有角色</option>
                                <option value="admin">管理员</option>
                                <option value="user">普通用户</option>
                            </select>
                        </div>
                        <button onclick="openUserModal('add')" 
                                style="padding: 10px 20px; background: #4f46e5; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 8px; box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);">
                            <span>➕</span>
                            <span>添加用户</span>
                        </button>
                    </div>

                    <!-- 用户表格 -->
                    <div class="users-table" style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                                <tr>
                                    <th style="padding: 15px; text-align: left; font-weight: 600;">ID</th>
                                    <th style="padding: 15px; text-align: left; font-weight: 600;">用户名</th>
                                    <th style="padding: 15px; text-align: left; font-weight: 600;">邮箱</th>
                                    <th style="padding: 15px; text-align: left; font-weight: 600;">角色</th>
                                    <th style="padding: 15px; text-align: left; font-weight: 600;">状态</th>
                                    <th style="padding: 15px; text-align: left; font-weight: 600;">创建时间</th>
                                    <th style="padding: 15px; text-align: center; font-weight: 600;">操作</th>
                                </tr>
                            </thead>
                            <tbody id="userTableBody">
                                <tr style="border-bottom: 1px solid #f3f4f6; transition: background 0.2s;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                    <td style="padding: 15px;">#1001</td>
                                    <td style="padding: 15px; font-weight: 500;">👑 admin</td>
                                    <td style="padding: 15px;">admin@example.com</td>
                                    <td style="padding: 15px;"><span style="background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">管理员</span></td>
                                    <td style="padding: 15px;"><span style="background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">✅ 正常</span></td>
                                    <td style="padding: 15px; color: #64748b;">2024-01-15</td>
                                    <td style="padding: 15px; text-align: center;">
                                        <button onclick="openUserModal('edit', 1001)" style="padding: 6px 12px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; margin-right: 5px; font-size: 12px;">✏️ 编辑</button>
                                        <button onclick="deleteUser(1001)" style="padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px;">🗑️ 删除</button>
                                    </td>
                                </tr>
                                <tr style="border-bottom: 1px solid #f3f4f6;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                    <td style="padding: 15px;">#1002</td>
                                    <td style="padding: 15px; font-weight: 500;">👤 zhangsan</td>
                                    <td style="padding: 15px;">zhangsan@example.com</td>
                                    <td style="padding: 15px;"><span style="background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">普通用户</span></td>
                                    <td style="padding: 15px;"><span style="background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">✅ 正常</span></td>
                                    <td style="padding: 15px; color: #64748b;">2024-03-20</td>
                                    <td style="padding: 15px; text-align: center;">
                                        <button onclick="openUserModal('edit', 1002)" style="padding: 6px 12px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; margin-right: 5px; font-size: 12px;">✏️ 编辑</button>
                                        <button onclick="deleteUser(1002)" style="padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px;">🗑️ 删除</button>
                                    </td>
                                </tr>
                                <tr style="border-bottom: 1px solid #f3f4f6;" onmouseover="this.style.background='#f9fafb'" onmouseout="this.style.background='white'">
                                    <td style="padding: 15px;">#1003</td>
                                    <td style="padding: 15px; font-weight: 500;">👤 lisi</td>
                                    <td style="padding: 15px;">lisi@example.com</td>
                                    <td style="padding: 15px;"><span style="background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">普通用户</span></td>
                                    <td style="padding: 15px;"><span style="background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">🚫 禁用</span></td>
                                    <td style="padding: 15px; color: #64748b;">2024-05-10</td>
                                    <td style="padding: 15px; text-align: center;">
                                        <button onclick="openUserModal('edit', 1003)" style="padding: 6px 12px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; margin-right: 5px; font-size: 12px;">✏️ 编辑</button>
                                        <button onclick="deleteUser(1003)" style="padding: 6px 12px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 12px;">🗑️ 删除</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- 分页 -->
                    <div id="paginationContainer" style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center;">
                        <!-- 分页将由JavaScript动态渲染 -->
                    </div>
                </div>

                <!-- 用户模态框 -->
                <div id="userModal" class="modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999; align-items: center; justify-content: center;">
                    <div class="modal-content" style="background: white; border-radius: 12px; padding: 30px; width: 500px; max-width: 90%; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h3 id="modalTitle" style="margin: 0; color: #1f2937;">➕ 添加用户</h3>
                            <button onclick="closeUserModal()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #9ca3af;">&times;</button>
                        </div>
                        <form id="userForm" onsubmit="submitUserForm(event)">
                            <div style="margin-bottom: 15px;">
                                <label style="display: block; margin-bottom: 5px; font-weight: 500; color: #374151;">👤 用户名</label>
                                <input type="text" id="username" required style="width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;" placeholder="请输入用户名">
                            </div>
                            <div style="margin-bottom: 15px;">
                                <label style="display: block; margin-bottom: 5px; font-weight: 500; color: #374151;">📧 邮箱</label>
                                <input type="email" id="email" required style="width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;" placeholder="请输入邮箱">
                            </div>
                            <div style="margin-bottom: 15px;">
                                <label style="display: block; margin-bottom: 5px; font-weight: 500; color: #374151;">🔑 密码</label>
                                <input type="password" id="password" style="width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;" placeholder="请输入密码">
                            </div>
                            <div style="margin-bottom: 15px;">
                                <label style="display: block; margin-bottom: 5px; font-weight: 500; color: #374151;">🎭 角色</label>
                                <select id="role" required style="width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;">
                                    <option value="user">普通用户</option>
                                    <option value="admin">管理员</option>
                                </select>
                            </div>
                            <div style="margin-bottom: 20px;">
                                <label style="display: block; margin-bottom: 5px; font-weight: 500; color: #374151;">🟢 状态</label>
                                <select id="status" required style="width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;">
                                    <option value="active">正常</option>
                                    <option value="inactive">禁用</option>
                                </select>
                            </div>
                            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                                <button type="button" onclick="closeUserModal()" style="padding: 10px 20px; background: #e5e7eb; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;">取消</button>
                                <button type="submit" style="padding: 10px 20px; background: #4f46e5; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600;">保存</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
        }
        
        // 系统日志的内容模板
        if (toolId === 'system-logs') {
            return `
                <div class="tool-header">
                    <h3>📋 系统日志</h3>
                    <p>查看系统运行日志和操作记录</p>
                </div>
                <div class="tool-body" style="padding: 20px;">
                    <div class="logs-section">
                        <h4>📊 日志统计</h4>
                        <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                            <div class="stat-card" style="background: #f0f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6;">
                                <div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">总记录数</div>
                                <div style="font-size: 24px; font-weight: bold; color: #3b82f6;">1,234</div>
                            </div>
                            <div class="stat-card" style="background: #f0fdf4; padding: 15px; border-radius: 8px; border-left: 4px solid #22c55e;">
                                <div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">成功操作</div>
                                <div style="font-size: 24px; font-weight: bold; color: #22c55e;">1,180</div>
                            </div>
                            <div class="stat-card" style="background: #fef2f2; padding: 15px; border-radius: 8px; border-left: 4px solid #ef4444;">
                                <div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">错误记录</div>
                                <div style="font-size: 24px; font-weight: bold; color: #ef4444;">54</div>
                            </div>
                            <div class="stat-card" style="background: #fffbeb; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                                <div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">警告信息</div>
                                <div style="font-size: 24px; font-weight: bold; color: #f59e0b;">12</div>
                            </div>
                        </div>
                    </div>

                    <div class="logs-section">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h4>📝 日志列表</h4>
                            <div style="display: flex; gap: 10px;">
                                <select style="padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px;">
                                    <option>所有级别</option>
                                    <option>INFO</option>
                                    <option>WARNING</option>
                                    <option>ERROR</option>
                                    <option>DEBUG</option>
                                </select>
                                <button style="padding: 8px 16px; background: #4f46e5; color: white; border: none; border-radius: 6px; cursor: pointer;">
                                    🔄 刷新
                                </button>
                            </div>
                        </div>
                        
                        <div class="logs-table" style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead style="background: #f9fafb;">
                                    <tr>
                                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; font-weight: 600; color: #374151;">时间</th>
                                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; font-weight: 600; color: #374151;">级别</th>
                                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; font-weight: 600; color: #374151;">模块</th>
                                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; font-weight: 600; color: #374151;">消息</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">2025-10-16 14:32:15</td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;"><span style="background: #dbeafe; color: #1e40af; padding: 4px 8px; border-radius: 4px; font-size: 12px;">INFO</span></td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">用户认证</td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">用户登录成功</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">2025-10-16 14:28:42</td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;"><span style="background: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 4px; font-size: 12px;">SUCCESS</span></td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">文件转换</td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">文件转换完成: report.pdf</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">2025-10-16 14:15:23</td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;"><span style="background: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 4px; font-size: 12px;">WARNING</span></td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">系统监控</td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">CPU使用率较高: 85%</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">2025-10-16 13:45:11</td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;"><span style="background: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-size: 12px;">ERROR</span></td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">文件转换</td>
                                        <td style="padding: 12px; border-bottom: 1px solid #f3f4f6;">文件格式不支持: invalid.xyz</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 12px;">2025-10-16 13:22:05</td>
                                        <td style="padding: 12px;"><span style="background: #dbeafe; color: #1e40af; padding: 4px 8px; border-radius: 4px; font-size: 12px;">INFO</span></td>
                                        <td style="padding: 12px;">系统启动</td>
                                        <td style="padding: 12px;">应用程序启动成功</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <div style="margin-top: 15px; text-align: center;">
                            <button style="padding: 8px 20px; background: white; border: 1px solid #d1d5db; border-radius: 6px; cursor: pointer;">
                                加载更多
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // 默认返回空内容
        return '<div class="tool-body"><p style="text-align: center; padding: 40px; color: #999;">工具内容加载中...</p></div>';
    },
    
    /**
     * 显示页签容器
     * @param {string} pageType - 页面类型
     */
    showTabsContainer(pageType) {
        console.log('显示页签容器:', pageType);
        const elements = this.getPageElements(pageType);
        const tabsContainer = document.getElementById(elements.container);
        const placeholder = document.getElementById(elements.placeholder);
        
        if (tabsContainer) {
            tabsContainer.style.display = 'flex';
        }
        if (placeholder) {
            placeholder.style.display = 'none';
        }
    },
    
    /**
     * 隐藏页签容器
     * @param {string} pageType - 页面类型
     */
    hideTabsContainer(pageType) {
        const elements = this.getPageElements(pageType);
        const tabsContainer = document.getElementById(elements.container);
        const placeholder = document.getElementById(elements.placeholder);
        
        if (tabsContainer) {
            tabsContainer.style.display = 'none';
        }
        if (placeholder) {
            placeholder.style.display = 'block';
        }
    }
};

/**
 * 全局函数：打开新页签
 * 供HTML onclick调用
 * @param {string} toolId - 工具ID
 * @param {string} title - 页签标题
 */
function openTab(toolId, title) {
    TabManager.openTab(toolId, title);
}

// 页面加载完成后初始化页签管理器
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM加载完成，初始化页签系统');
    TabManager.init();
    
    // 自动展开文件处理分类
    const fileProcessingContent = document.getElementById('file-processing-content');
    if (fileProcessingContent) {
        fileProcessingContent.style.display = 'block';
    }
    const fileProcessingToggle = document.getElementById('file-processing-toggle');
    if (fileProcessingToggle) {
        fileProcessingToggle.textContent = '▼';
    }
});
