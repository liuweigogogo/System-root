#!/usr/bin/env python3
"""
文件转换功能依赖安装脚本
安装所需的Python包
"""

import subprocess
import sys
import os

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 安装失败: {e}")
        return False

def main():
    """主函数"""
    print("=== 文件转换功能依赖安装 ===")
    print()
    
    # 必需的包列表
    required_packages = [
        "python-docx",      # Word文档处理
        "docx2pdf",         # Word转PDF
        "pdf2docx",         # PDF转Word
        "python-pptx",      # PowerPoint处理
        "pptx2pdf",         # PowerPoint转PDF
        "pandas",           # Excel/CSV处理
        "openpyxl",         # Excel文件支持
        "Pillow",           # 图片处理
        "PyPDF2"           # PDF处理

    ]
    
    print("开始安装依赖包...")
    print()
    
    success_count = 0
    total_count = len(required_packages)
    
    for package in required_packages:
        print(f"正在安装 {package}...")
        if install_package(package):
            success_count += 1
        print()
    
    print("=== 安装结果 ===")
    print(f"成功安装: {success_count}/{total_count}")
    print(f"失败安装: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 所有依赖包安装成功！")
        print("现在可以使用文件转换功能了。")
    else:
        print(f"\n⚠️  有 {total_count - success_count} 个包安装失败。")
        print("请检查网络连接或手动安装失败的包。")
    
    print("\n=== 使用说明 ===")
    print("1. 启动应用: python app.py")
    print("2. 访问转换页面: http://localhost:5000/converter")
    print("3. 支持的转换格式:")
    print("   - Word ↔ PDF")
    print("   - PowerPoint ↔ PDF")
    print("   - Excel ↔ CSV ↔ JSON")
    print("   - 图片格式互转 (JPG, PNG, WebP等)")

if __name__ == "__main__":
    main()
