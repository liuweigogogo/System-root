"""
修复所有Python文件中的相对导入问题
将 from ..xxx 改为 from xxx
"""
import os
import re

def fix_imports_in_file(filepath):
    """修复单个文件中的导入"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 将 from ..xxx 替换为 from xxx
    original_content = content
    content = re.sub(r'from \.\.(\w+)', r'from \1', content)
    
    # 只有内容发生变化时才写入
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已修复: {filepath}")
        return True
    return False

def main():
    """遍历所有Python文件并修复导入"""
    base_dir = r"d:\Program Files\JetBrains\PythonProject\project-root\frotend"
    fixed_count = 0
    
    for root, dirs, files in os.walk(base_dir):
        # 跳过 __pycache__ 目录
        if '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_imports_in_file(filepath):
                    fixed_count += 1
    
    print(f"\n总共修复了 {fixed_count} 个文件")

if __name__ == '__main__':
    main()
