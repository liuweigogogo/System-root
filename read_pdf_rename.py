import os
import pdfplumber
import re


# PDF 提取金额的函数
def extract_amount_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        # 遍历 PDF 的所有页面
        for page in pdf.pages:
            text += page.extract_text()
            # print(text)
        # 正则匹配金额
        match = re.search(r'（小写）¥(\d+(\.\d{1,2})?)', text)
        if match:
            return match.group(1)  # 返回提取到的金额
        return None


# 批量处理文件并重命名
def batch_rename_pdfs(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            amount = extract_amount_from_pdf(pdf_path)
            if amount:
                # 根据金额重命名文件
                new_name = f"{amount}.pdf"
                new_path = os.path.join(directory, new_name)
                os.rename(pdf_path, new_path)
                print(f"Renamed: {filename} -> {new_name}")
            else:
                print(f"Amount not found in: {filename}")

# 设置目标文件夹路径
# pdf_folder = r'C:\Users\liu\Desktop\FaPiao'
# # print(extract_amount_from_pdf(pdf_folder))
# batch_rename_pdfs(pdf_folder)

#
#
# text = "<h1>Title</h1><p>Paragraph</p>"
# # 贪婪模式会匹配整个字符串
# match_greedy = re.findall(r'<.*>', text)
# print(match_greedy)  # 输出：['<h1>Title</h1><p>Paragraph</p>']
#
#
#
# import secrets
#
# # 生成一个 64 字符长的随机密钥
# secret_key = secrets.token_urlsafe(64)
# print(secret_key)
# text='abc123x yz '
# print(text.strip())


print(bool(0))