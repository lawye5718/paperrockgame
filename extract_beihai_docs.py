#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import fitz  # PyMuPDF
from pathlib import Path
import subprocess

def preprocess_with_ocrmypdf(input_pdf, output_pdf):
    """
    使用OCRmyPDF预处理PDF文件
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
        
        # 构建OCRmyPDF命令
        cmd = [
            'ocrmypdf',
            '-l', 'chi_sim',  # 简体中文
            '--optimize', '3',  # 最高级别压缩
            '--output-type', 'pdf',
            input_pdf,
            output_pdf
        ]
        
        # 执行OCRmyPDF
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5分钟超时
        
        if result.returncode == 0:
            print(f"OCR处理成功: {output_pdf}")
            return True
        else:
            print(f"OCR处理失败: {input_pdf}")
            print(f"错误信息: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"OCR处理超时: {input_pdf}")
        return False
    except Exception as e:
        print(f"OCR处理出错: {str(e)}")
        return False

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

def is_toc_page(pdf_document, page_num):
    """
    判断页面是否为目录页（第一行包含"目录"两个字）
    对于扫描版PDF，我们需要通过OCR识别或简单地检查是否有文本
    因为我们处理的是扫描版PDF，所以这里简化处理，只检查页面是否有文本内容
    """
    try:
        page = pdf_document[page_num]
        text = page.get_text().strip()
        lines = text.split('\n')
        if lines:
            first_line = lines[0].strip()
            return "目录" in first_line
        return False
    except Exception as e:
        print(f"检查第{page_num + 1}页是否为目录页时出错: {str(e)}")
        return False

def process_pdf_file(pdf_path, output_base_dir, ocr_output_base_dir):
    """
    处理单个PDF文件，提取封面和目录页
    """
    try:
        # 创建OCR处理后的PDF保存路径
        relative_path = os.path.relpath(pdf_path, "/Volumes/TU260Pro/北海案件资料_处理中/原始卷")
        ocr_pdf_path = os.path.join(ocr_output_base_dir, relative_path)
        
        # 先进行OCR预处理
        print(f"正在进行OCR预处理: {pdf_path}")
        if not preprocess_with_ocrmypdf(pdf_path, ocr_pdf_path):
            print(f"OCR预处理失败，跳过文件: {pdf_path}")
            return False
        
        # 创建输出目录，保持相对路径结构（用于图片提取）
        output_dir = os.path.join(output_base_dir, os.path.splitext(relative_path)[0])
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"正在处理: {pdf_path}")
        print(f"输出目录: {output_dir}")
        
        # 打开OCR处理后的PDF文件
        pdf_document = fitz.open(ocr_pdf_path)
        total_pages = len(pdf_document)
        
        # 提取封面（第一页）
        print("提取封面...")
        cover_images = extract_images_from_page(pdf_document, 0, output_dir)
        
        # 提取目录页
        toc_pages = []
        print("查找目录页...")
        # 通常目录在前10页内，从第2页开始查找（封面之后）
        for page_num in range(1, min(10, total_pages)):
            if is_toc_page(pdf_document, page_num):
                toc_pages.append(page_num)
                print(f"找到目录页: 第{page_num + 1}页")
                # 提取目录页图片
                extract_images_from_page(pdf_document, page_num, output_dir)
            elif toc_pages:  # 如果之前找到过目录页，但现在不是目录页了，就停止查找
                print(f"目录结束于第{page_num}页")
                break
        
        # 生成摘要文件
        summary_file = os.path.join(output_dir, "summary.md")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# {os.path.basename(pdf_path)} 内容摘要\n\n")
            f.write(f"## 文件信息\n")
            f.write(f"- 原始文件: {pdf_path}\n")
            f.write(f"- OCR处理后文件: {ocr_pdf_path}\n")
            f.write(f"- 总页数: {total_pages}\n")
            f.write(f"- 封面页: 第1页 (提取了 {cover_images} 张图片)\n")
            f.write(f"- 目录页: {', '.join([f'第{p+1}页' for p in toc_pages]) if toc_pages else '未找到'}\n")
            f.write(f"\n## 说明\n")
            f.write("此PDF已完成OCR处理，可直接进行文本搜索和复制。\n")
        
        pdf_document.close()
        print(f"完成处理: {pdf_path}\n")
        return True
        
    except Exception as e:
        print(f"处理文件 {pdf_path} 时出错: {str(e)}")
        return False

def main():
    # 定义输入和输出文件夹
    input_folder = "/Volumes/TU260Pro/北海案件资料_处理中/原始卷"
    ocr_output_folder = "/Users/yuanliang/Downloads/beihai_ocr_processed"
    extract_output_folder = "/Users/yuanliang/Downloads/beihai_extracted"
    
    print("=" * 60)
    print("北海案件PDF文档OCR预处理及封面目录提取工具")
    print("=" * 60)
    print(f"输入文件夹: {input_folder}")
    print(f"OCR处理后文件夹: {ocr_output_folder}")
    print(f"图片提取输出文件夹: {extract_output_folder}")
    
    # 创建输出文件夹
    os.makedirs(ocr_output_folder, exist_ok=True)
    os.makedirs(extract_output_folder, exist_ok=True)
    
    # 查找所有PDF文件
    pdf_files = []
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.pdf') and not file.startswith('._'):
                full_path = os.path.join(root, file)
                pdf_files.append(full_path)
    
    print(f"\n找到 {len(pdf_files)} 个PDF文件")
    
    # 处理所有文件
    print("\n开始处理所有文件...")
    processed_count = 0
    success_count = 0
    for i, pdf_file in enumerate(pdf_files):
        try:
            processed_count += 1
            if process_pdf_file(pdf_file, extract_output_folder, ocr_output_folder):
                success_count += 1
        except Exception as e:
            print(f"处理文件 {pdf_file} 时发生错误: {str(e)}")
    
    print(f"\n处理完成!")
    print(f"总文件数: {len(pdf_files)}")
    print(f"已处理: {processed_count} 个文件")
    print(f"成功处理: {success_count} 个文件")
    print(f"OCR处理后文件目录: {ocr_output_folder}")
    print(f"图片提取输出目录: {extract_output_folder}")

if __name__ == "__main__":
    main()