#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import fitz  # PyMuPDF
from pathlib import Path

def extract_images_from_page(pdf_document, page_num, output_dir):
    """
    从PDF页面提取图片（用于扫描版PDF）
    """
    try:
        page = pdf_document[page_num]
        
        # 创建页面目录
        page_dir = os.path.join(output_dir, f"page_{page_num + 1}")
        os.makedirs(page_dir, exist_ok=True)
        
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
        
        # 如果页面没有嵌入图像，尝试将整个页面渲染为图像
        if image_count == 0:
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            image_filename = os.path.join(page_dir, f"page_as_image.png")
            pix.save(image_filename)
            pix = None
            image_count = 1
        
        return image_count
    except Exception as e:
        print(f"处理第{page_num + 1}页时出错: {str(e)}")
        return 0

def process_pdf_file(pdf_path, output_base_dir):
    """
    处理单个PDF文件（针对扫描版PDF）
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
        cover_images = extract_images_from_page(pdf_document, 0, output_dir)
        
        # 生成摘要文件
        summary_file = os.path.join(output_dir, "summary.md")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# {os.path.basename(pdf_path)} 内容摘要\n\n")
            f.write(f"## 文件信息\n")
            f.write(f"- 总页数: {total_pages}\n")
            f.write(f"- 封面页: 第1页\n")
            f.write(f"- 封面图片数: {cover_images}\n")
            f.write(f"\n## 说明\n")
            f.write("此PDF为扫描版，无文本层。已提取页面图像供后续OCR处理。\n")
            f.write("建议使用OCR工具（如OCRmyPDF、Tesseract等）对图像进行文字识别。\n")
        
        pdf_document.close()
        print(f"完成处理: {pdf_path}\n")
        
    except Exception as e:
        print(f"处理文件 {pdf_path} 时出错: {str(e)}")

def main():
    # 定义输入和输出文件夹
    input_folder = "/Volumes/TU260Pro/北海案件资料_处理中/原始卷"
    output_folder = "/Users/yuanliang/Downloads/pdf_extracted_content"
    
    print("=" * 60)
    print("PDF扫描版处理工具")
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
    
    # 处理前3个文件作为示例
    print("\n开始处理前3个文件...")
    for i, pdf_file in enumerate(pdf_files[:3]):
        process_pdf_file(pdf_file, output_folder)
    
    print(f"\n处理完成! 已处理 {min(3, len(pdf_files))} 个文件")
    print(f"输出目录: {output_folder}")
    print("\n注意: 这些PDF文件为扫描版，无文本层。")
    print("请使用OCR工具对提取的图像进行文字识别。")

if __name__ == "__main__":
    main()