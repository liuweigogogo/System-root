# 文件格式转换功能使用说明

## 📋 功能概述

本系统提供了完整的文件格式转换功能，支持多种文件格式之间的相互转换，包括：

- **文档转换**: Word ↔ PDF
- **演示文稿转换**: PowerPoint ↔ PDF  
- **表格转换**: Excel ↔ CSV ↔ JSON
- **图片转换**: JPG, PNG, WebP 等格式互转

## 🚀 快速开始

### 1. 安装依赖

```bash
# 运行依赖安装脚本
python install_converter_deps.py
```

### 2. 启动应用

```bash
python app.py
```

### 3. 访问转换页面

打开浏览器访问: `http://localhost:5000/converter`

## 📁 文件结构

```
frotend/
├── services/
│   └── FileConverterService.py      # 文件转换服务核心模块
├── controllers/
│   └── FileConverterController.py   # 文件转换控制器
├── templates/
│   └── file_converter.html         # 转换页面模板
├── css/
│   └── converter.css               # 转换页面样式
├── js/
│   └── file_converter.js           # 转换页面脚本
└── app.py                          # 主应用文件（已更新路由）
```

## 🔧 核心模块说明

### FileConverterService.py

**主要功能**:
- 文件格式转换的核心逻辑
- 支持多种转换格式
- 依赖库检查和错误处理
- 批量转换功能

**关键方法**:
```python
# 转换单个文件
convert_file(file_path, target_format, output_path=None)

# 批量转换
batch_convert(file_list, target_format, output_dir=None)

# 获取文件信息
get_file_info(file_path)

# 获取支持的转换格式
get_supported_conversions()
```

### FileConverterController.py

**主要功能**:
- 处理HTTP请求
- 文件上传和下载
- 参数验证和错误处理
- 临时文件管理

**API端点**:
- `GET /api/convert/supported` - 获取支持的转换格式
- `POST /api/convert/single` - 单文件转换
- `POST /api/convert/batch` - 批量转换
- `POST /api/convert/info` - 获取文件信息
- `GET /api/convert/download/<filename>` - 下载转换文件

## 🎯 支持的转换格式

### 文档转换
- `docx_to_pdf`: Word文档转PDF
- `pdf_to_docx`: PDF转Word文档

### 演示文稿转换
- `pptx_to_pdf`: PowerPoint转PDF
- `pdf_to_pptx`: PDF转PowerPoint

### 表格转换
- `xlsx_to_csv`: Excel转CSV
- `csv_to_xlsx`: CSV转Excel
- `xlsx_to_json`: Excel转JSON
- `json_to_xlsx`: JSON转Excel

### 图片转换
- `jpg_to_png`: JPG转PNG
- `png_to_jpg`: PNG转JPG
- `webp_to_png`: WebP转PNG
- `png_to_webp`: PNG转WebP

## 💻 前端功能

### 单文件转换
- 支持拖拽上传
- 自动检测文件类型
- 动态更新目标格式选项
- 实时转换进度显示

### 批量转换
- 多文件同时上传
- 批量处理进度跟踪
- 转换结果统计

### 文件信息查看
- 文件基本信息显示
- 支持的转换格式提示
- 文件大小和修改时间

### 操作历史
- 本地存储操作记录
- 历史记录导出功能
- 操作结果统计

## 🔍 代码跳转说明

### 服务层跳转
```
FileConverterService.py
├── convert_file() → _perform_conversion()
├── _perform_conversion() → _convert_xxx_to_xxx()
├── _convert_docx_to_pdf() → docx2pdf_convert()
├── _convert_pdf_to_docx() → Pdf2DocxConverter()
├── _convert_pptx_to_pdf() → pptx2pdf_convert()
├── _convert_xlsx_to_csv() → pandas.read_excel()
├── _convert_csv_to_xlsx() → pandas.to_excel()
└── _convert_image() → PIL.Image.open()
```

### 控制器层跳转
```
FileConverterController.py
├── convert_file() → FileConverterService.convert_file()
├── batch_convert() → FileConverterService.batch_convert()
├── get_file_info() → FileConverterService.get_file_info()
└── _send_converted_file() → send_file()
```

### 前端跳转
```
file_converter.js
├── FileConverter.init() → loadSupportedConversions()
├── handleSingleConvert() → fetch('/api/convert/single')
├── handleBatchConvert() → fetch('/api/convert/batch')
├── handleFileInfo() → fetch('/api/convert/info')
└── updateTargetFormats() → 动态更新选择框
```

## 🛠️ 依赖库说明

### 必需依赖
- `python-docx`: Word文档处理
- `docx2pdf`: Word转PDF
- `pdf2docx`: PDF转Word
- `python-pptx`: PowerPoint处理
- `pptx2pdf`: PowerPoint转PDF
- `pandas`: 表格数据处理
- `openpyxl`: Excel文件支持
- `Pillow`: 图片处理
- `PyPDF2`: PDF处理

### 安装命令
```bash
pip install python-docx docx2pdf pdf2docx python-pptx pptx2pdf pandas openpyxl Pillow PyPDF2
```

## 🧪 测试

### 运行测试脚本
```bash
python test_file_converter.py
```

### 测试内容
- 依赖库检查
- 转换格式验证
- 文件转换功能测试
- 错误处理测试

## 📝 使用示例

### Python代码示例
```python
from frotend.services.FileConverterService import FileConverterService

# 创建转换服务
converter = FileConverterService()

# 转换单个文件
result = converter.convert_file('input.docx', 'pdf')
if result['success']:
    print(f"转换成功: {result['output_path']}")

# 批量转换
files = ['file1.xlsx', 'file2.xlsx']
result = converter.batch_convert(files, 'csv')
print(f"批量转换完成: 成功{result['success_count']}个")
```

### API调用示例
```javascript
// 单文件转换
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('target_format', 'pdf');

fetch('/api/convert/single', {
    method: 'POST',
    body: formData
})
.then(response => response.blob())
.then(blob => {
    // 处理下载文件
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'converted.pdf';
    a.click();
});
```

## ⚠️ 注意事项

1. **文件大小限制**: 建议单个文件不超过100MB
2. **格式兼容性**: 某些复杂格式可能转换效果不理想
3. **临时文件**: 转换后的文件会临时存储，定期清理
4. **错误处理**: 转换失败时会显示具体错误信息
5. **依赖检查**: 首次使用前请确保所有依赖库已安装

## 🔧 故障排除

### 常见问题

1. **依赖库缺失**
   - 运行 `python install_converter_deps.py`
   - 手动安装缺失的包

2. **转换失败**
   - 检查文件格式是否支持
   - 确认文件没有损坏
   - 查看错误日志

3. **文件下载失败**
   - 检查文件路径是否正确
   - 确认文件没有被删除

4. **页面无法访问**
   - 确认应用已启动
   - 检查端口是否被占用
   - 查看控制台错误信息

## 📞 技术支持

如遇到问题，请：
1. 查看错误日志
2. 运行测试脚本
3. 检查依赖库安装
4. 参考本文档的故障排除部分
