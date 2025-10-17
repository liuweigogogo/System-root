/**
 * 集成的文件转换器
 * 
 * 职责：
 * - 处理文件选择和验证
 * - 调用后端API进行文件转换
 * - 显示转换结果、错误信息和预览
 * - 提供下载功能
 * - 管理转换历史记录
 * 
 * 功能特性：
 * - 完整的错误处理和用户反馈
 * - 支持文件预览（文本、图片）
 * - 转换历史记录
 * - 详细的转换进度提示
 */

class IntegratedFileConverter {
    constructor() {
        // 初始化转换器状态
        this.supportedFormats = {}  // 支持的转换格式映射
        this.conversionHistory = this.loadHistory()  // 转换历史记录
        this.currentFile = null  // 当前选择的文件
        this.convertedFileBlob = null  // 转换后的文件Blob对象
        this.convertedFileName = ''  // 转换后的文件名
        
        // 初始化组件
        this.init()
    }

    /**
     * 初始化转换器
     * 
     * 流程：
     * 1. 加载支持的转换格式
     * 2. 绑定事件监听器
     * 3. 加载历史记录
     */
    init() {
        console.log('📦 初始化文件转换器...')
        this.loadSupportedFormats()
        this.bindEvents()
        this.renderHistory()
    }

    /**
     * 加载支持的转换格式
     * 
     * 从后端API获取支持的文件转换类型
     */
    async loadSupportedFormats() {
        try {
            const response = await fetch('/api/convert/supported')
            const data = await response.json()
            
            if (data.success) {
                this.supportedFormats = data.conversions
                console.log('✅ 加载转换格式成功', this.supportedFormats)
            } else {
                this.showError('加载转换格式失败: ' + data.message)
            }
        } catch (error) {
            console.error('❌ 加载转换格式失败:', error)
            this.showError('网络错误，无法加载转换格式')
        }
    }

    /**
     * 绑定事件监听器
     * 
     * 监听：
     * - 文件选择变化
     * - 表单提交
     */
    bindEvents() {
        // 文件选择变化时更新目标格式选项
        const fileInput = document.getElementById('converterFileInput')
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileSelect(e)
            })
        }

        // 表单提交
        const form = document.getElementById('fileConvertForm')
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault()
                this.handleConversion()
            })
        }
    }

    /**
     * 处理文件选择
     * 
     * 当用户选择文件时：
     * 1. 获取文件信息
     * 2. 更新目标格式下拉框
     * 3. 显示文件详情
     * 
     * @param {Event} event - 文件选择事件
     */
    handleFileSelect(event) {
        const file = event.target.files[0]
        if (!file) {
            return
        }

        this.currentFile = file
        console.log('📄 选择文件:', file.name, '大小:', this.formatFileSize(file.size))

        // 获取文件扩展名
        const ext = this.getFileExtension(file.name)
        console.log('📎 文件类型:', ext)

        // 更新目标格式选项
        this.updateTargetFormats(ext)
    }

    /**
     * 更新目标格式下拉框
     * 
     * 根据源文件类型，显示可以转换的目标格式
     * 
     * @param {string} sourceExt - 源文件扩展名
     */
    updateTargetFormats(sourceExt) {
        const select = document.getElementById('targetFormat')
        if (!select) return

        // 清空选项
        select.innerHTML = '<option value="">请选择目标格式</option>'

        // 查找支持的转换类型
        const availableConversions = []
        Object.entries(this.supportedFormats).forEach(([key, conversion]) => {
            if (conversion.from === sourceExt) {
                availableConversions.push(conversion)
            }
        })

        // 添加选项
        if (availableConversions.length === 0) {
            select.innerHTML = '<option value="">该文件类型暂不支持转换</option>'
            console.warn('⚠️ 文件类型不支持:', sourceExt)
        } else {
            availableConversions.forEach(conv => {
                const option = document.createElement('option')
                option.value = conv.to
                option.textContent = `${conv.to.toUpperCase()} - ${conv.description}`
                select.appendChild(option)
            })
            console.log('✅ 可用转换:', availableConversions.length, '种')
        }
    }

    /**
     * 处理文件转换
     * 
     * 流程：
     * 1. 验证表单数据
     * 2. 创建FormData
     * 3. 调用后端API
     * 4. 处理响应
     * 5. 显示结果或错误
     */
    async handleConversion() {
        // 1. 验证表单
        const fileInput = document.getElementById('converterFileInput')
        const targetFormat = document.getElementById('targetFormat').value

        if (!fileInput || !fileInput.files[0]) {
            this.showError('请选择要转换的文件')
            return
        }

        if (!targetFormat) {
            this.showError('请选择目标格式')
            return
        }

        const file = fileInput.files[0]
        console.log(`🔄 开始转换: ${file.name} → ${targetFormat.toUpperCase()}`)

        // 2. 显示加载状态
        this.setLoading(true)
        this.hideResult()
        this.hideError()

        // 3. 创建表单数据
        const formData = new FormData()
        formData.append('file', file)
        formData.append('target_format', targetFormat)

        try {
            // 4. 调用API
            const response = await fetch('/api/convert/single', {
                method: 'POST',
                body: formData
            })

            // 5. 处理响应
            if (response.ok) {
                // 转换成功 - 处理文件下载
                const blob = await response.blob()
                const filename = this.getConvertedFileName(file.name, targetFormat)
                
                // 保存转换结果
                this.convertedFileBlob = blob
                this.convertedFileName = filename

                // 显示成功结果
                this.showSuccess(file.name, targetFormat, blob, filename)
                
                // 添加到历史
                this.addToHistory(file.name, targetFormat, 'success', null)
                
                console.log('✅ 转换成功!')
            } else {
                // 转换失败 - 显示错误信息
                const errorData = await response.json()
                const errorMessage = errorData.message || '转换失败'
                const errorCode = errorData.error_code || 'UNKNOWN_ERROR'
                
                this.showError(
                    `转换失败: ${errorMessage}`,
                    `错误代码: ${errorCode}\n文件: ${file.name}\n目标格式: ${targetFormat}`
                )
                
                // 添加到历史
                this.addToHistory(file.name, targetFormat, 'failed', errorMessage)
                
                console.error('❌ 转换失败:', errorMessage, errorCode)
            }
        } catch (error) {
            // 网络错误
            console.error('❌ 网络错误:', error)
            this.showError(
                '网络错误，请检查连接后重试',
                `详细信息: ${error.message}`
            )
            this.addToHistory(file.name, targetFormat, 'error', '网络错误')
        } finally {
            // 6. 恢复UI状态
            this.setLoading(false)
        }
    }

    /**
     * 显示转换成功结果
     * 
     * @param {string} originalName - 原始文件名
     * @param {string} targetFormat - 目标格式
     * @param {Blob} blob - 转换后的文件Blob
     * @param {string} filename - 转换后的文件名
     */
    showSuccess(originalName, targetFormat, blob, filename) {
        const resultDiv = document.getElementById('conversionResult')
        const contentDiv = document.getElementById('resultContent')
        
        if (!resultDiv || !contentDiv) return

        // 构建结果HTML
        contentDiv.innerHTML = `
            <div class="success-message">
                <div class="success-icon">✅</div>
                <h4>转换成功！</h4>
                <p class="success-details">
                    <strong>${originalName}</strong> 已成功转换为 <strong>${targetFormat.toUpperCase()}</strong> 格式
                </p>
                <div class="success-info">
                    <div class="info-item">
                        <span class="info-label">文件名:</span>
                        <span class="info-value">${filename}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">文件大小:</span>
                        <span class="info-value">${this.formatFileSize(blob.size)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">转换时间:</span>
                        <span class="info-value">${new Date().toLocaleString()}</span>
                    </div>
                </div>
                <div class="success-actions">
                    <button onclick="converterInstance.downloadFile()" class="btn-download">
                        📥 立即下载
                    </button>
                    <button onclick="converterInstance.previewFile()" class="btn-preview">
                        👁️ 预览文件
                    </button>
                </div>
            </div>
        `

        // 显示结果区域
        resultDiv.style.display = 'block'
        
        // 滚动到结果区域
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }

    /**
     * 下载转换后的文件
     */
    downloadFile() {
        if (!this.convertedFileBlob || !this.convertedFileName) {
            alert('没有可下载的文件')
            return
        }

        console.log('📥 下载文件:', this.convertedFileName)

        // 创建下载链接
        const url = window.URL.createObjectURL(this.convertedFileBlob)
        const a = document.createElement('a')
        a.href = url
        a.download = this.convertedFileName
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)

        console.log('✅ 下载完成')
    }

    /**
     * 预览转换后的文件
     * 
     * 支持预览：
     * - 文本文件（txt, csv, json等）
     * - 图片文件（jpg, png等）
     * - PDF文件
     */
    previewFile() {
        if (!this.convertedFileBlob) {
            alert('没有可预览的文件')
            return
        }

        const ext = this.getFileExtension(this.convertedFileName)
        console.log('👁️ 预览文件:', this.convertedFileName, '类型:', ext)

        // 根据文件类型预览
        if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(ext)) {
            // 图片预览
            this.previewImage()
        } else if (['txt', 'csv', 'json'].includes(ext)) {
            // 文本预览
            this.previewText()
        } else if (ext === 'pdf') {
            // PDF预览
            this.previewPDF()
        } else {
            // 不支持预览，直接下载
            alert('该文件类型不支持预览，请下载后查看')
            this.downloadFile()
        }
    }

    /**
     * 预览图片文件
     */
    previewImage() {
        const url = window.URL.createObjectURL(this.convertedFileBlob)
        const previewWindow = window.open('', '_blank')
        previewWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>${this.convertedFileName} - 预览</title>
                <style>
                    body {
                        margin: 0;
                        padding: 20px;
                        background: #f0f0f0;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        font-family: Arial, sans-serif;
                    }
                    h2 { color: #333; }
                    img {
                        max-width: 100%;
                        max-height: 80vh;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        background: white;
                        padding: 10px;
                    }
                </style>
            </head>
            <body>
                <h2>📷 图片预览: ${this.convertedFileName}</h2>
                <img src="${url}" alt="${this.convertedFileName}">
            </body>
            </html>
        `)
        console.log('✅ 图片预览打开')
    }

    /**
     * 预览文本文件
     */
    async previewText() {
        try {
            const text = await this.convertedFileBlob.text()
            const previewWindow = window.open('', '_blank')
            previewWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>${this.convertedFileName} - 预览</title>
                    <style>
                        body {
                            margin: 0;
                            padding: 20px;
                            background: #f9f9f9;
                            font-family: 'Courier New', monospace;
                        }
                        h2 {
                            color: #333;
                            font-family: Arial, sans-serif;
                        }
                        pre {
                            background: white;
                            padding: 20px;
                            border-radius: 5px;
                            border: 1px solid #ddd;
                            overflow-x: auto;
                            white-space: pre-wrap;
                            word-wrap: break-word;
                        }
                    </style>
                </head>
                <body>
                    <h2>📄 文本预览: ${this.convertedFileName}</h2>
                    <pre>${text.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
                </body>
                </html>
            `)
            console.log('✅ 文本预览打开')
        } catch (error) {
            console.error('❌ 文本预览失败:', error)
            alert('文本预览失败')
        }
    }

    /**
     * 预览PDF文件
     */
    previewPDF() {
        const url = window.URL.createObjectURL(this.convertedFileBlob)
        window.open(url, '_blank')
        console.log('✅ PDF预览打开')
    }

    /**
     * 显示错误信息
     * 
     * @param {string} message - 错误消息
     * @param {string} details - 详细信息（可选）
     */
    showError(message, details = '') {
        const errorDiv = document.getElementById('conversionError')
        const contentDiv = document.getElementById('errorContent')
        
        if (!errorDiv || !contentDiv) {
            alert(message)
            return
        }

        contentDiv.innerHTML = `
            <div class="error-message">
                <div class="error-icon">❌</div>
                <h4>${message}</h4>
                ${details ? `<pre class="error-details">${details}</pre>` : ''}
                <p class="error-hint">💡 提示：请检查文件格式是否正确，或尝试其他文件</p>
            </div>
        `

        errorDiv.style.display = 'block'
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }

    /**
     * 隐藏结果区域
     */
    hideResult() {
        const resultDiv = document.getElementById('conversionResult')
        if (resultDiv) {
            resultDiv.style.display = 'none'
        }
    }

    /**
     * 隐藏错误区域
     */
    hideError() {
        const errorDiv = document.getElementById('conversionError')
        if (errorDiv) {
            errorDiv.style.display = 'none'
        }
    }

    /**
     * 设置加载状态
     * 
     * @param {boolean} loading - 是否加载中
     */
    setLoading(loading) {
        const button = document.querySelector('.btn-convert')
        const btnText = button.querySelector('.btn-text')
        const btnLoading = button.querySelector('.btn-loading')
        
        if (loading) {
            button.disabled = true
            button.style.opacity = '0.6'
            btnText.style.display = 'none'
            btnLoading.style.display = 'inline'
        } else {
            button.disabled = false
            button.style.opacity = '1'
            btnText.style.display = 'inline'
            btnLoading.style.display = 'none'
        }
    }

    // ==================== 历史记录管理 ====================

    /**
     * 添加到历史记录
     * 
     * @param {string} filename - 文件名
     * @param {string} targetFormat - 目标格式
     * @param {string} status - 状态 (success/failed/error)
     * @param {string} errorMsg - 错误消息（可选）
     */
    addToHistory(filename, targetFormat, status, errorMsg = null) {
        const record = {
            id: Date.now(),
            filename,
            targetFormat,
            status,
            errorMsg,
            timestamp: new Date().toISOString()
        }

        this.conversionHistory.unshift(record)
        
        // 限制历史记录数量
        if (this.conversionHistory.length > 50) {
            this.conversionHistory = this.conversionHistory.slice(0, 50)
        }

        this.saveHistory()
        this.renderHistory()
    }

    /**
     * 渲染历史记录
     */
    renderHistory() {
        const historyDiv = document.getElementById('conversionHistory')
        if (!historyDiv) return

        if (this.conversionHistory.length === 0) {
            historyDiv.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">暂无转换记录</p>'
            return
        }

        historyDiv.innerHTML = this.conversionHistory.slice(0, 10).map(record => `
            <div class="history-item ${record.status}">
                <div class="history-icon">${this.getStatusIcon(record.status)}</div>
                <div class="history-content">
                    <div class="history-file">${record.filename} → ${record.targetFormat.toUpperCase()}</div>
                    <div class="history-time">${new Date(record.timestamp).toLocaleString()}</div>
                    ${record.errorMsg ? `<div class="history-error">${record.errorMsg}</div>` : ''}
                </div>
            </div>
        `).join('')
    }

    /**
     * 获取状态图标
     * 
     * @param {string} status - 状态
     * @returns {string} 图标
     */
    getStatusIcon(status) {
        const icons = {
            'success': '✅',
            'failed': '❌',
            'error': '⚠️'
        }
        return icons[status] || '❓'
    }

    /**
     * 加载历史记录
     * 
     * @returns {Array} 历史记录数组
     */
    loadHistory() {
        try {
            const data = localStorage.getItem('fileConverterHistory')
            return data ? JSON.parse(data) : []
        } catch (error) {
            console.error('加载历史记录失败:', error)
            return []
        }
    }

    /**
     * 保存历史记录
     */
    saveHistory() {
        try {
            localStorage.setItem('fileConverterHistory', JSON.stringify(this.conversionHistory))
        } catch (error) {
            console.error('保存历史记录失败:', error)
        }
    }

    // ==================== 工具方法 ====================

    /**
     * 获取文件扩展名
     * 
     * @param {string} filename - 文件名
     * @returns {string} 扩展名（小写）
     */
    getFileExtension(filename) {
        return filename.split('.').pop().toLowerCase()
    }

    /**
     * 生成转换后的文件名
     * 
     * @param {string} originalName - 原始文件名
     * @param {string} targetFormat - 目标格式
     * @returns {string} 新文件名
     */
    getConvertedFileName(originalName, targetFormat) {
        const nameWithoutExt = originalName.replace(/\.[^/.]+$/, '')
        return `${nameWithoutExt}.${targetFormat}`
    }

    /**
     * 格式化文件大小
     * 
     * @param {number} bytes - 字节数
     * @returns {string} 格式化后的大小
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B'
        const k = 1024
        const sizes = ['B', 'KB', 'MB', 'GB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
}

// 创建全局实例
let converterInstance = null

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 检查是否在实用工具页面
    if (document.getElementById('fileConvertForm')) {
        converterInstance = new IntegratedFileConverter()
        console.log('✅ 文件转换器已初始化')
    }
})
