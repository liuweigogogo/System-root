#!/usr/bin/env python3
"""
文件转换功能测试脚本
测试各种文件格式转换功能
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'frotend'))

from frotend.services.FileConverterService import FileConverterService

def create_test_files():
    """创建测试文件"""
    test_dir = tempfile.mkdtemp(prefix='converter_test_')
    test_files = {}
    
    # 创建测试CSV文件
    csv_content = "姓名,年龄,城市\n张三,25,北京\n李四,30,上海\n王五,28,广州"
    csv_path = os.path.join(test_dir, 'test.csv')
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    test_files['csv'] = csv_path
    
    # 创建测试JSON文件
    json_content = '''[
    {"姓名": "张三", "年龄": 25, "城市": "北京"},
    {"姓名": "李四", "年龄": 30, "城市": "上海"},
    {"姓名": "王五", "年龄": 28, "城市": "广州"}
]'''
    json_path = os.path.join(test_dir, 'test.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_content)
    test_files['json'] = json_path
    
    return test_dir, test_files

def test_converter_service():
    """测试文件转换服务"""
    print("=== 文件转换服务测试 ===")
    print()
    
    # 创建转换服务实例
    converter = FileConverterService()
    
    # 检查依赖
    print("1. 检查依赖库:")
    for lib, available in converter.dependencies.items():
        status = "✅ 可用" if available else "❌ 不可用"
        print(f"   {lib}: {status}")
    print()
    
    # 获取支持的转换格式
    print("2. 支持的转换格式:")
    conversions = converter.get_supported_conversions()
    for key, info in conversions.items():
        print(f"   {key}: {info['description']}")
    print()
    
    # 创建测试文件
    print("3. 创建测试文件...")
    test_dir, test_files = create_test_files()
    print(f"   测试目录: {test_dir}")
    print()
    
    # 测试文件信息获取
    print("4. 测试文件信息获取:")
    for file_type, file_path in test_files.items():
        info = converter.get_file_info(file_path)
        if info['success']:
            print(f"   {file_type}: {info['file_name']} ({info['file_size']} bytes)")
        else:
            print(f"   {file_type}: 获取信息失败 - {info['message']}")
    print()
    
    # 测试转换功能
    print("5. 测试文件转换:")
    test_conversions = [
        ('csv', 'xlsx', 'CSV转Excel'),
        ('json', 'xlsx', 'JSON转Excel'),
    ]
    
    for source_ext, target_ext, description in test_conversions:
        if source_ext in test_files:
            source_path = test_files[source_ext]
            print(f"   测试 {description}...")
            
            result = converter.convert_file(source_path, target_ext)
            if result['success']:
                print(f"   ✅ 转换成功: {result['output_path']}")
                # 检查输出文件是否存在
                if os.path.exists(result['output_path']):
                    file_size = os.path.getsize(result['output_path'])
                    print(f"      输出文件大小: {file_size} bytes")
                else:
                    print(f"      ⚠️ 输出文件不存在")
            else:
                print(f"   ❌ 转换失败: {result['message']}")
        else:
            print(f"   ⚠️ 跳过 {description} (测试文件不存在)")
        print()
    
    # 清理测试文件
    print("6. 清理测试文件...")
    try:
        import shutil
        shutil.rmtree(test_dir)
        print("   ✅ 测试文件已清理")
    except Exception as e:
        print(f"   ⚠️ 清理失败: {e}")
    
    print("\n=== 测试完成 ===")

def test_conversion_capabilities():
    """测试转换能力"""
    print("=== 转换能力测试 ===")
    print()
    
    converter = FileConverterService()
    
    # 按类别显示转换能力
    categories = {
        '文档转换': ['docx_to_pdf', 'pdf_to_docx'],
        '演示文稿转换': ['pptx_to_pdf', 'pdf_to_pptx'],
        '表格转换': ['xlsx_to_csv', 'csv_to_xlsx', 'xlsx_to_json', 'json_to_xlsx'],
        '图片转换': ['jpg_to_png', 'png_to_jpg', 'webp_to_png', 'png_to_webp']
    }
    
    for category, conversions in categories.items():
        print(f"{category}:")
        for conv_key in conversions:
            if conv_key in converter.SUPPORTED_CONVERSIONS:
                conv_info = converter.SUPPORTED_CONVERSIONS[conv_key]
                print(f"  ✅ {conv_info['from']} → {conv_info['to']}: {conv_info['description']}")
            else:
                print(f"  ❌ {conv_key}: 不支持")
        print()

if __name__ == "__main__":
    print("文件转换功能测试")
    print("=" * 50)
    print()
    
    try:
        test_converter_service()
        print()
        test_conversion_capabilities()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
