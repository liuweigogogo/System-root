/**
 * 实用工具模块
 * 包含工具分类管理、工具切换、文件处理等功能
 */

/**
 * 分类折叠/展开功能
 * 控制工具分类的显示和隐藏
 * @param {string} categoryId - 分类ID（如'file-processing', 'image-processing'）
 */
function toggleCategory(categoryId) {
    const content = document.getElementById(categoryId + '-content');
    const toggle = document.getElementById(categoryId + '-toggle');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggle.textContent = '▼';
    } else {
        content.style.display = 'none';
        toggle.textContent = '▶';
    }
}

/**
 * 工具切换功能
 * 在右侧内容区域显示选中的工具
 * @param {string} toolId - 工具ID（如'batch-rename', 'file-converter'）
 */
function showTool(toolId) {
    // 隐藏所有工具内容
    const tools = document.querySelectorAll('.tool-content');
    tools.forEach(tool => tool.classList.remove('active'));
    
    // 移除所有工具项的active状态
    const toolItems = document.querySelectorAll('.tool-item');
    toolItems.forEach(item => item.classList.remove('active'));
    
    // 显示指定工具
    const targetTool = document.getElementById(toolId + '-tool');
    if (targetTool) {
        targetTool.classList.add('active');
    }
    
    // 激活对应的工具项
    const activeItem = document.querySelector(`[onclick="showTool('${toolId}')"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
}

/**
 * 更新文件列表显示
 * 当用户选择文件后更新文件列表UI
 */
function updateFileList() {
    const files = document.getElementById('fileInput').files;
    const fileList = document.getElementById('fileList');
    
    selectedFiles = Array.from(files);
    fileList.innerHTML = '';
    
    selectedFiles.forEach(file => {
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = `
            <span class="file-name">${file.name}</span>
            <span class="file-size">${(file.size / 1024).toFixed(1)} KB</span>
        `;
        fileList.appendChild(div);
    });
    
    // 自动更新预览
    previewRename();
}

/**
 * 更新重命名规则输入框
 * 根据选择的重命名规则显示相应的输入框
 */
function updateRuleInput() {
    const rule = document.getElementById('renameRule').value;
    const ruleInput = document.getElementById('ruleInput');
    
    switch(rule) {
        case 'prefix':
            ruleInput.innerHTML = '<input type="text" id="prefixText" placeholder="输入前缀" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px;">';
            break;
        case 'suffix':
            ruleInput.innerHTML = '<input type="text" id="suffixText" placeholder="输入后缀" style="width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px;">';
            break;
        case 'replace':
            ruleInput.innerHTML = '<input type="text" id="oldText" placeholder="原文本" style="width: 48%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; margin-right: 2%;"><input type="text" id="newText" placeholder="新文本" style="width: 48%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px;">';
            break;
        case 'sequence':
            ruleInput.innerHTML = '<input type="text" id="sequencePrefix" placeholder="前缀（可选）" style="width: 48%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; margin-right: 2%;"><input type="number" id="startNumber" placeholder="起始数字" value="1" min="1" style="width: 48%; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px;">';
            break;
    }
    
    // 重新绑定事件监听器
    const newRuleInput = document.getElementById('ruleInput');
    if (newRuleInput) {
        newRuleInput.addEventListener('input', previewRename);
    }
}

/**
 * 预览重命名效果
 * 根据选择的重命名规则和参数预览重命名后的文件名
 */
function previewRename() {
    const rule = document.getElementById('renameRule').value;
    const previewList = document.getElementById('previewList');
    
    if (selectedFiles.length === 0) {
        previewList.innerHTML = '<div class="preview-item">请先选择文件</div>';
        return;
    }
    
    previewList.innerHTML = '';
    
    selectedFiles.forEach((file, index) => {
        const div = document.createElement('div');
        div.className = 'preview-item';
        
        let newName = file.name;
        const nameWithoutExt = file.name.substring(0, file.name.lastIndexOf('.'));
        const ext = file.name.substring(file.name.lastIndexOf('.'));
        
        switch(rule) {
            case 'prefix':
                const prefix = document.getElementById('prefixText')?.value || '';
                newName = prefix + file.name;
                break;
            case 'suffix':
                const suffix = document.getElementById('suffixText')?.value || '';
                newName = nameWithoutExt + suffix + ext;
                break;
            case 'replace':
                const oldText = document.getElementById('oldText')?.value || '';
                const newText = document.getElementById('newText')?.value || '';
                newName = file.name.replace(new RegExp(oldText, 'g'), newText);
                break;
            case 'sequence':
                const seqPrefix = document.getElementById('sequencePrefix')?.value || '';
                const startNum = parseInt(document.getElementById('startNumber')?.value || '1');
                newName = seqPrefix + (startNum + index).toString().padStart(3, '0') + ext;
                break;
        }
        
        div.innerHTML = `<strong>${file.name}</strong> → <em>${newName}</em>`;
        previewList.appendChild(div);
    });
}

/**
 * 执行文件重命名
 * 根据预览结果创建重命名后的文件
 */
function executeRename() {
    if (selectedFiles.length === 0) {
        alert('请先选择文件');
        return;
    }
    
    // 创建重命名后的文件列表
    renamedFiles = [];
    const rule = document.getElementById('renameRule').value;
    
    selectedFiles.forEach((file, index) => {
        let newName = file.name;
        const nameWithoutExt = file.name.substring(0, file.name.lastIndexOf('.'));
        const ext = file.name.substring(file.name.lastIndexOf('.'));
        
        switch(rule) {
            case 'prefix':
                const prefix = document.getElementById('prefixText')?.value || '';
                newName = prefix + file.name;
                break;
            case 'suffix':
                const suffix = document.getElementById('suffixText')?.value || '';
                newName = nameWithoutExt + suffix + ext;
                break;
            case 'replace':
                const oldText = document.getElementById('oldText')?.value || '';
                const newText = document.getElementById('newText')?.value || '';
                newName = file.name.replace(new RegExp(oldText, 'g'), newText);
                break;
            case 'sequence':
                const seqPrefix = document.getElementById('sequencePrefix')?.value || '';
                const startNum = parseInt(document.getElementById('startNumber')?.value || '1');
                newName = seqPrefix + (startNum + index).toString().padStart(3, '0') + ext;
                break;
        }
        
        // 创建重命名后的文件对象
        const renamedFile = new File([file], newName, { type: file.type });
        renamedFiles.push(renamedFile);
    });
    
    // 显示下载按钮
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.style.display = 'inline-block';
    }
    
    alert('重命名完成！点击"下载重命名后的文件"按钮下载。');
}

/**
 * 下载重命名后的文件
 * 将重命名后的文件逐个下载到用户设备
 */
function downloadRenamedFiles() {
    if (renamedFiles.length === 0) {
        alert('没有可下载的文件');
        return;
    }
    
    // 逐个下载文件（简化版实现）
    renamedFiles.forEach((file, index) => {
        const url = URL.createObjectURL(file);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.name;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // 添加延迟避免浏览器阻止多个下载
        if (index < renamedFiles.length - 1) {
            setTimeout(() => {}, 100);
        }
    });
}
