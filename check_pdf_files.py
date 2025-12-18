#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import PyPDF2

def check_pdf_file(filepath):
    """
    检查PDF文件是否可以正常打开
    """
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            # 尝试读取第一页（如果存在）
            if num_pages > 0:
                first_page = pdf_reader.pages[0]
                text = first_page.extract_text()
            return True, num_pages, "文件可以正常打开"
    except Exception as e:
        return False, 0, str(e)

def main():
    # 定义失败文件夹路径
    failed_folder = "/Volumes/TU260Pro/北海案件资料_处理中/处理失败无密码文件"
    
    print("=" * 60)
    print("PDF文件检查工具")
    print("=" * 60)
    
    print(f"检查文件夹: {failed_folder}")
    
    # 获取所有PDF文件
    pdf_files = []
    for root, dirs, files in os.walk(failed_folder):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                pdf_files.append((file, full_path))
    
    print(f"\n找到 {len(pdf_files)} 个PDF文件")
    
    # 检查每个PDF文件
    valid_count = 0
    invalid_count = 0
    
    for filename, filepath in pdf_files:
        is_valid, num_pages, message = check_pdf_file(filepath)
        if is_valid:
            print(f"✓ {filename} - 有效 ({num_pages} 页)")
            valid_count += 1
        else:
            print(f"✗ {filename} - 无效 ({message})")
            invalid_count += 1
    
    print(f"\n检查完成!")
    print(f"有效文件: {valid_count} 个")
    print(f"无效文件: {invalid_count} 个")

if __name__ == "__main__":
    main()