/**
 * 文件转换工具 JavaScript
 * 处理文件上传、转换、下载等功能
 */

class FileConverter {
    constructor() {
        this.supportedConversions = {};
        this.operationHistory = JSON.parse(localStorage.getItem('converterHistory') || '[]');
        this.init();
    }

    /**
     * 初始化文件转换器
     */
    init() {
        this.loadSupportedConversions();
        this.bindEvents();
        this.loadHistory();
        this.setupFileDragDrop();
    }

    /**
     * 加载支持的转换格式
     */
    async loadSupportedConversions() {
        try {
            const response = await fetch('/api/convert/supported');
            const data = await response.json();
            
            if (data.success) {
                this.supportedConversions = data.conversions;
                this.renderFormatGrid();
                this.populateFormatSelects();
            } else {
                this.showMessage('加载转换格式失败: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('加载转换格式失败:', error);
            this.showMessage('网络错误，请检查连接', 'error');
        }
    }

    /**
     * 渲染格式网格
     */
    renderFormatGrid() {
        const formatGrid = document.getElementById('formatGrid');
        const formatGroups = this.groupConversionsByCategory();
        
        formatGrid.innerHTML = Object.entries(formatGroups).map(([category, conversions]) => `
            <div class="format-card">
                <h3>${this.getCategoryTitle(category)}</h3>
                <p>${this.getCategoryDescription(category)}</p>
                <div class="supported-formats">
                    ${conversions.map(conv => 
                        `<span class="format-tag">${conv.from} → ${conv.to}</span>`
                    ).join('')}
                </div>
            </div>
        `).join('');
    }

    /**
     * 按类别分组转换格式
     */
    groupConversionsByCategory() {
        const groups = {};
        
        Object.entries(this.supportedConversions).forEach(([key, conversion]) => {
            const category = this.getConversionCategory(conversion.from);
            if (!groups[category]) {
                groups[category] = [];
            }
            groups[category].push(conversion);
        });
        
        return groups;
    }

    /**
     * 获取转换类别
     */
    getConversionCategory(format) {
        if (['docx', 'pdf'].includes(format)) return 'document';
        if (['pptx'].includes(format)) return 'presentation';
        if (['xlsx', 'csv', 'json'].includes(format)) return 'spreadsheet';
        if (['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp'].includes(format)) return 'image';
        return 'other';
    }

    /**
     * 获取类别标题
     */
    getCategoryTitle(category) {
        const titles = {
            'document': '📄 文档转换',
            'presentation': '📊 演示文稿转换',
            'spreadsheet': '📈 表格转换',
            'image': '🖼️ 图片转换',
            'other': '📁 其他格式'
        };
        return titles[category] || '📁 其他格式';
    }

    /**
     * 获取类别描述
     */
    getCategoryDescription(category) {
        const descriptions = {
            'document': '支持Word文档和PDF之间的相互转换',
            'presentation': '支持PowerPoint演示文稿转换',
            'spreadsheet': '支持Excel、CSV、JSON等表格格式转换',
            'image': '支持各种图片格式之间的相互转换',
            'other': '支持其他文件格式转换'
        };
        return descriptions[category] || '支持其他文件格式转换';
    }

    /**
     * 填充格式选择框
     */
    populateFormatSelects() {
        const selects = ['singleTargetFormat', 'batchTargetFormat'];
        
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            const currentFile = selectId === 'singleTargetFormat' ? 
                document.getElementById('singleFile') : 
                document.getElementById('batchFiles');
            
            // 清空现有选项
            select.innerHTML = '<option value="">请选择目标格式</option>';
            
            // 添加格式选项
            Object.entries(this.supportedConversions).forEach(([key, conversion]) => {
                const option = document.createElement('option');
                option.value = conversion.to;
                option.textContent = `${conversion.to.toUpperCase()} - ${conversion.description}`;
                select.appendChild(option);
            });
        });
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 单文件转换
        document.getElementById('singleConvertForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSingleConvert();
        });

        // 批量转换
        document.getElementById('batchConvertForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleBatchConvert();
        });

        // 文件信息查看
        document.getElementById('fileInfoForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFileInfo();
        });

        // 清空历史
        document.getElementById('clearHistory').addEventListener('click', () => {
            this.clearHistory();
        });

        // 导出历史
        document.getElementById('exportHistory').addEventListener('click', () => {
            this.exportHistory();
        });

        // 文件选择变化时更新目标格式
        document.getElementById('singleFile').addEventListener('change', (e) => {
            this.updateTargetFormats(e.target, 'singleTargetFormat');
        });

        document.getElementById('batchFiles').addEventListener('change', (e) => {
            this.updateTargetFormats(e.target, 'batchTargetFormat');
        });
    }

    /**
     * 更新目标格式选项
     */
    updateTargetFormats(fileInput, targetSelectId) {
        const files = fileInput.files;
        if (files.length === 0) return;

        const select = document.getElementById(targetSelectId);
        const file = files[0];
        const fileExt = file.name.split('.').pop().toLowerCase();
        
        // 清空现有选项
        select.innerHTML = '<option value="">请选择目标格式</option>';
        
        // 添加可用的转换选项
        Object.entries(this.supportedConversions).forEach(([key, conversion]) => {
            if (conversion.from === fileExt) {
                const option = document.createElement('option');
                option.value = conversion.to;
                option.textContent = `${conversion.to.toUpperCase()} - ${conversion.description}`;
                select.appendChild(option);
            }
        });
    }

    /**
     * 处理单文件转换
     */
    async handleSingleConvert() {
        const form = document.getElementById('singleConvertForm');
        const formData = new FormData(form);
        
        if (!formData.get('file').name) {
            this.showMessage('请选择要转换的文件', 'error');
            return;
        }

        if (!formData.get('target_format')) {
            this.showMessage('请选择目标格式', 'error');
            return;
        }

        this.showLoading(true);
        this.setButtonLoading('singleConvertForm', true);

        try {
            const response = await fetch('/api/convert/single', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                // 处理文件下载
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = this.getDownloadFilename(formData.get('file').name, formData.get('target_format'));
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                this.showMessage('文件转换成功！', 'success');
                this.addToHistory('单文件转换', formData.get('file').name, formData.get('target_format'), '成功');
            } else {
                const errorData = await response.json();
                this.showMessage('转换失败: ' + errorData.message, 'error');
                this.addToHistory('单文件转换', formData.get('file').name, formData.get('target_format'), '失败');
            }
        } catch (error) {
            console.error('转换失败:', error);
            this.showMessage('网络错误，请重试', 'error');
            this.addToHistory('单文件转换', formData.get('file').name, formData.get('target_format'), '失败');
        } finally {
            this.showLoading(false);
            this.setButtonLoading('singleConvertForm', false);
        }
    }

    /**
     * 处理批量转换
     */
    async handleBatchConvert() {
        const form = document.getElementById('batchConvertForm');
        const formData = new FormData(form);
        
        const files = formData.getAll('files');
        if (files.length === 0) {
            this.showMessage('请选择要转换的文件', 'error');
            return;
        }

        if (!formData.get('target_format')) {
            this.showMessage('请选择目标格式', 'error');
            return;
        }

        this.showLoading(true);
        this.setButtonLoading('batchConvertForm', true);

        try {
            const response = await fetch('/api/convert/batch', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                this.showMessage(`批量转换完成！成功: ${data.result.success_count}, 失败: ${data.result.failed_count}`, 'success');
                this.addToHistory('批量转换', `${files.length}个文件`, formData.get('target_format'), 
                    `成功${data.result.success_count}个，失败${data.result.failed_count}个`);
            } else {
                this.showMessage('批量转换失败: ' + data.message, 'error');
                this.addToHistory('批量转换', `${files.length}个文件`, formData.get('target_format'), '失败');
            }
        } catch (error) {
            console.error('批量转换失败:', error);
            this.showMessage('网络错误，请重试', 'error');
            this.addToHistory('批量转换', `${files.length}个文件`, formData.get('target_format'), '失败');
        } finally {
            this.showLoading(false);
            this.setButtonLoading('batchConvertForm', false);
        }
    }

    /**
     * 处理文件信息查看
     */
    async handleFileInfo() {
        const form = document.getElementById('fileInfoForm');
        const formData = new FormData(form);
        
        if (!formData.get('file').name) {
            this.showMessage('请选择要查看的文件', 'error');
            return;
        }

        try {
            const response = await fetch('/api/convert/info', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                this.displayFileInfo(data.file_info);
                this.showMessage('文件信息获取成功', 'success');
            } else {
                this.showMessage('获取文件信息失败: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('获取文件信息失败:', error);
            this.showMessage('网络错误，请重试', 'error');
        }
    }

    /**
     * 显示文件信息
     */
    displayFileInfo(fileInfo) {
        const resultDiv = document.getElementById('fileInfoResult');
        resultDiv.innerHTML = `
            <div class="file-info-item">
                <span class="file-info-label">文件名:</span>
                <span class="file-info-value">${fileInfo.file_name}</span>
            </div>
            <div class="file-info-item">
                <span class="file-info-label">文件大小:</span>
                <span class="file-info-value">${this.formatFileSize(fileInfo.file_size)}</span>
            </div>
            <div class="file-info-item">
                <span class="file-info-label">文件类型:</span>
                <span class="file-info-value">${fileInfo.file_extension.toUpperCase()}</span>
            </div>
            <div class="file-info-item">
                <span class="file-info-label">修改时间:</span>
                <span class="file-info-value">${new Date(fileInfo.modified_time * 1000).toLocaleString()}</span>
            </div>
            <div class="file-info-item">
                <span class="file-info-label">支持的转换:</span>
                <span class="file-info-value">${fileInfo.supported_conversions.join(', ')}</span>
            </div>
        `;
        resultDiv.style.display = 'block';
    }

    /**
     * 格式化文件大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * 获取下载文件名
     */
    getDownloadFilename(originalName, targetFormat) {
        const nameWithoutExt = originalName.replace(/\.[^/.]+$/, '');
        return `${nameWithoutExt}.${targetFormat}`;
    }

    /**
     * 设置文件拖拽功能
     */
    setupFileDragDrop() {
        const dropZones = document.querySelectorAll('input[type="file"]');
        
        dropZones.forEach(input => {
            const parent = input.parentElement;
            parent.classList.add('file-drop-zone');
            
            parent.addEventListener('dragover', (e) => {
                e.preventDefault();
                parent.classList.add('dragover');
            });
            
            parent.addEventListener('dragleave', () => {
                parent.classList.remove('dragover');
            });
            
            parent.addEventListener('drop', (e) => {
                e.preventDefault();
                parent.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    input.dispatchEvent(new Event('change'));
                }
            });
        });
    }

    /**
     * 显示/隐藏加载遮罩
     */
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    /**
     * 设置按钮加载状态
     */
    setButtonLoading(formId, loading) {
        const form = document.getElementById(formId);
        const button = form.querySelector('button[type="submit"]');
        const btnText = button.querySelector('.btn-text');
        const btnLoading = button.querySelector('.btn-loading');
        
        if (loading) {
            button.classList.add('loading');
            button.disabled = true;
        } else {
            button.classList.remove('loading');
            button.disabled = false;
        }
    }

    /**
     * 显示消息提示
     */
    showMessage(message, type = 'info') {
        const toast = document.getElementById('messageToast');
        const messageText = toast.querySelector('.message-text');
        
        messageText.textContent = message;
        toast.className = `message-toast ${type}`;
        toast.style.display = 'flex';
        
        // 3秒后自动隐藏
        setTimeout(() => {
            toast.style.display = 'none';
        }, 3000);
    }

    /**
     * 添加到操作历史
     */
    addToHistory(operation, filename, targetFormat, status) {
        const historyItem = {
            id: Date.now(),
            operation,
            filename,
            targetFormat,
            status,
            timestamp: new Date().toISOString()
        };
        
        this.operationHistory.unshift(historyItem);
        
        // 限制历史记录数量
        if (this.operationHistory.length > 100) {
            this.operationHistory = this.operationHistory.slice(0, 100);
        }
        
        this.saveHistory();
        this.loadHistory();
    }

    /**
     * 加载操作历史
     */
    loadHistory() {
        const historyList = document.getElementById('historyList');
        
        if (this.operationHistory.length === 0) {
            historyList.innerHTML = '<p style="text-align: center; color: #666;">暂无操作历史</p>';
            return;
        }
        
        historyList.innerHTML = this.operationHistory.map(item => `
            <div class="history-item">
                <div class="history-item-header">
                    <span class="history-item-title">${item.operation}</span>
                    <span class="history-item-time">${new Date(item.timestamp).toLocaleString()}</span>
                </div>
                <div class="history-item-details">
                    文件: ${item.filename} | 目标格式: ${item.targetFormat} | 状态: ${item.status}
                </div>
            </div>
        `).join('');
    }

    /**
     * 清空操作历史
     */
    clearHistory() {
        if (confirm('确定要清空所有操作历史吗？')) {
            this.operationHistory = [];
            this.saveHistory();
            this.loadHistory();
            this.showMessage('操作历史已清空', 'success');
        }
    }

    /**
     * 导出操作历史
     */
    exportHistory() {
        if (this.operationHistory.length === 0) {
            this.showMessage('没有操作历史可导出', 'warning');
            return;
        }
        
        const csvContent = [
            '操作类型,文件名,目标格式,状态,时间',
            ...this.operationHistory.map(item => 
                `"${item.operation}","${item.filename}","${item.targetFormat}","${item.status}","${item.timestamp}"`
            )
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `converter_history_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showMessage('操作历史已导出', 'success');
    }

    /**
     * 保存操作历史到本地存储
     */
    saveHistory() {
        localStorage.setItem('converterHistory', JSON.stringify(this.operationHistory));
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new FileConverter();
});
