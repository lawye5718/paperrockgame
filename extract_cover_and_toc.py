#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import fitz  # PyMuPDF
import re
from pathlib import Path

def extract_text_and_images_from_page(pdf_document, page_num, output_dir):
    """
    从PDF页面提取文字和图片
    """
    try:
        page = pdf_document[page_num]
        
        # 创建页面目录
        page_dir = os.path.join(output_dir, f"page_{page_num + 1}")
        os.makedirs(page_dir, exist_ok=True)
        
        # 提取文字
        text = page.get_text()
        text_file = os.path.join(page_dir, f"page_{page_num + 1}.md")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"# 第{page_num + 1}页\n\n")
            f.write(text)
        
        # 提取图片
        image_list = page.get_images()
        image_count = 0
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(pdf_document, xref)
            
            # 保存图片
            if pix.n < 5:  # this is GRAY or RGB
                image_filename = os.path.join(page_dir, f"image_{img_index + 1}.png")
                pix.save(image_filename)
                image_count += 1
            else:  # CMYK: convert to RGB first
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                image_filename = os.path.join(page_dir, f"image_{img_index + 1}.png")
                pix1.save(image_filename)
                pix1 = None
                image_count += 1
            
            pix = None
        
        return text, image_count
    except Exception as e:
        print(f"处理第{page_num + 1}页时出错: {str(e)}")
        return "", 0

def is_toc_page(text):
    """
    判断页面是否为目录页（第一行包含"目录"两个字）
    """
    lines = text.strip().split('\n')
    if lines:
        first_line = lines[0].strip()
        return "目录" in first_line
    return False

def process_pdf_file(pdf_path, output_base_dir):
    """
    处理单个PDF文件
    """
    try:
        # 创建输出目录
        relative_path = os.path.relpath(pdf_path, "/Volumes/TU260Pro/北海案件资料_处理中/原始卷")
        output_dir = os.path.join(output_base_dir, os.path.splitext(relative_path)[0])
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"正在处理: {pdf_path}")
        print(f"输出目录: {output_dir}")
        
        # 打开PDF文件
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        
        # 提取封面（第一页）
        print("提取封面...")
        cover_text, cover_images = extract_text_and_images_from_page(pdf_document, 0, output_dir)
        
        # 提取目录页
        toc_pages = []
        print("查找目录页...")
        for page_num in range(1, min(10, total_pages)):  # 通常目录在前10页内
            page_text, page_images = extract_text_and_images_from_page(pdf_document, page_num, output_dir)
            if is_toc_page(page_text):
                toc_pages.append(page_num)
                print(f"找到目录页: 第{page_num + 1}页")
            elif toc_pages:  # 如果之前找到过目录页，但现在不是目录页了，就停止查找
                break
        
        # 生成摘要文件
        summary_file = os.path.join(output_dir, "summary.md")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# {os.path.basename(pdf_path)} 内容摘要\n\n")
            f.write(f"## 文件信息\n")
            f.write(f"- 总页数: {total_pages}\n")
            f.write(f"- 封面页: 第1页\n")
            f.write(f"- 目录页: {', '.join([f'第{p+1}页' for p in toc_pages]) if toc_pages else '未找到'}\n")
            f.write(f"\n## 封面内容\n")
            f.write(cover_text[:1000] + "..." if len(cover_text) > 1000 else cover_text)
            
            if toc_pages:
                f.write(f"\n## 目录内容\n")
                for page_num in toc_pages:
                    f.write(f"\n### 第{page_num + 1}页目录\n")
                    page = pdf_document[page_num]
                    toc_text = page.get_text()
                    f.write(toc_text[:1000] + "..." if len(toc_text) > 1000 else toc_text)
        
        pdf_document.close()
        print(f"完成处理: {pdf_path}\n")
        
    except Exception as e:
        print(f"处理文件 {pdf_path} 时出错: {str(e)}")

def main():
    # 定义输入和输出文件夹
    input_folder = "/Volumes/TU260Pro/北海案件资料_处理中/原始卷"
    output_folder = "/Users/yuanliang/Downloads/pdf_extracted_content"
    
    print("=" * 60)
    print("PDF封面和目录提取工具")
    print("=" * 60)
    print(f"输入文件夹: {input_folder}")
    print(f"输出文件夹: {output_folder}")
    
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)
    
    # 查找所有PDF文件
    pdf_files = []
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.pdf') and not file.startswith('._'):
                full_path = os.path.join(root, file)
                pdf_files.append(full_path)
    
    print(f"\n找到 {len(pdf_files)} 个PDF文件")
    
    # 处理前5个文件作为示例
    print("\n开始处理前5个文件...")
    for i, pdf_file in enumerate(pdf_files[:5]):
        process_pdf_file(pdf_file, output_folder)
    
    print(f"\n处理完成! 已处理 {min(5, len(pdf_files))} 个文件")
    print(f"输出目录: {output_folder}")

if __name__ == "__main__":
    main()