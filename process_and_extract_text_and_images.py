#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import numpy as np
import cv2
from pathlib import Path
from PIL import Image

def process_pdf_with_paddleocr(input_pdf, output_pdf):
    """
    使用PaddleOCR处理PDF文件
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
        
        # 打开原始PDF
        doc = fitz.open(input_pdf)
        
        # 创建新的PDF用于保存结果
        new_doc = fitz.open()
        
        # 初始化PaddleOCR
        ocr = PaddleOCR(lang='ch', use_gpu=False)  # 使用CPU进行OCR，避免GPU内存不足
        
        for page_num in range(len(doc)):
            # 获取页面
            page = doc[page_num]
            
            # 将页面转换为图像
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # 保存为图像
            img_data = pix.tobytes("png")
            img_array = np.frombuffer(img_data, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            # 使用PaddleOCR进行OCR
            result = ocr.ocr(img, cls=False)
            
            # 创建带有OCR层的新页面
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            
            # 将原始页面作为背景添加
            new_page.show_pdf_page(new_page.rect, doc, page_num)
            
            # 添加OCR文本层（隐藏文本）
            if result is not None:
                for line in result:
                    if line is not None:
                        for box in line:
                            if box is not None and len(box) > 1:
                                coords = box[0]
                                text = box[1][0]
                                
                                # 计算文本框位置
                                if coords is not None and len(coords) >= 4:
                                    x0, y0 = coords[0]
                                    x1, y1 = coords[2]
                                    
                                    # 添加文本
                                    rect = fitz.Rect(x0/2, y0/2, x1/2, y1/2)  # 除以2是因为我们用了2倍缩放
                                    new_page.insert_textbox(rect, text, fontsize=1, color=(0, 0, 0))
            
            pix = None
        
        # 保存新PDF
        new_doc.save(output_pdf)
        new_doc.close()
        doc.close()
        
        print(f"PaddleOCR处理成功: {output_pdf}")
        return True
        
    except Exception as e:
        print(f"PaddleOCR处理出错: {str(e)}")
        return False

def extract_text_and_images_from_page(pdf_document, page_num, output_dir, pdf_name):
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
        
        # 确定页面类型（封面或目录）
        page_type = "封面" if page_num == 0 else f"目录第{page_num}页"
        
        # 保存文字到MD文件
        md_filename = f"{pdf_name}_{page_type}.md"
        md_file = os.path.join(output_dir, md_filename)
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# {pdf_name} {page_type}\n\n")
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
        
        # 如果页面没有嵌入图像，尝试将整个页面渲染为图像
        if image_count == 0:
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            image_filename = os.path.join(page_dir, f"page_as_image.png")
            pix.save(image_filename)
            pix = None
            image_count = 1
        
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

def process_single_pdf(pdf_path, ocr_output_base_dir, extract_output_base_dir):
    """
    处理单个PDF文件
    """
    try:
        # 创建OCR处理后的PDF保存路径
        relative_path = os.path.relpath(pdf_path, "/Volumes/TU260Pro/北海案件资料_处理中/原始卷")
        ocr_pdf_path = os.path.join(ocr_output_base_dir, relative_path)
        
        # 先进行OCR预处理
        print(f"正在进行PaddleOCR预处理: {pdf_path}")
        if not process_pdf_with_paddleocr(pdf_path, ocr_pdf_path):
            print(f"PaddleOCR预处理失败，跳过文件: {pdf_path}")
            return False
        
        # 创建提取内容的输出目录
        extract_output_dir = os.path.join(extract_output_base_dir, os.path.splitext(relative_path)[0])
        os.makedirs(extract_output_dir, exist_ok=True)
        
        print(f"正在提取内容: {pdf_path}")
        print(f"OCR处理后文件: {ocr_pdf_path}")
        print(f"内容提取目录: {extract_output_dir}")
        
        # 打开OCR处理后的PDF文件
        pdf_document = fitz.open(ocr_pdf_path)
        total_pages = len(pdf_document)
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # 提取封面（第一页）
        print("提取封面...")
        cover_text, cover_images = extract_text_and_images_from_page(pdf_document, 0, extract_output_dir, pdf_name)
        
        # 提取目录页
        toc_pages = []
        print("查找目录页...")
        # 通常目录在前10页内，从第2页开始查找（封面之后）
        for page_num in range(1, min(10, total_pages)):
            page_text, page_images = extract_text_and_images_from_page(pdf_document, page_num, extract_output_dir, pdf_name)
            if is_toc_page(page_text):
                toc_pages.append(page_num)
                print(f"找到目录页: 第{page_num + 1}页")
            elif toc_pages:  # 如果之前找到过目录页，但现在不是目录页了，就停止查找
                print(f"目录结束于第{page_num + 1}页")
                break
        
        # 生成总体摘要文件
        summary_file = os.path.join(extract_output_dir, f"{pdf_name}_摘要.md")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# {pdf_name} 内容摘要\n\n")
            f.write(f"## 文件信息\n")
            f.write(f"- 原始文件: {pdf_path}\n")
            f.write(f"- OCR处理后文件: {ocr_pdf_path}\n")
            f.write(f"- 总页数: {total_pages}\n")
            f.write(f"- 封面页: 第1页\n")
            f.write(f"- 目录页: {', '.join([f'第{p+1}页' for p in toc_pages]) if toc_pages else '未找到'}\n")
            f.write(f"\n## 封面内容预览\n")
            f.write(cover_text[:500] + "..." if len(cover_text) > 500 else cover_text)
            
            if toc_pages:
                f.write(f"\n## 目录内容预览\n")
                for page_num in toc_pages:
                    f.write(f"\n### 第{page_num + 1}页目录\n")
                    page = pdf_document[page_num]
                    toc_text = page.get_text()
                    f.write(toc_text[:500] + "..." if len(toc_text) > 500 else toc_text)
        
        pdf_document.close()
        print(f"完成处理: {pdf_path}\n")
        return True
        
    except Exception as e:
        print(f"处理文件 {pdf_path} 时出错: {str(e)}")
        return False

def main():
    # 定义输入和输出文件夹
    input_folder = "/Volumes/TU260Pro/北海案件资料_处理中/原始卷"
    ocr_output_folder = "/Users/yuanliang/Downloads/beihai_ocr_processed_v2"
    extract_output_folder = "/Users/yuanliang/Downloads/beihai_extracted_v2"
    
    print("=" * 70)
    print("北海案件PDF文档OCR处理及封面目录提取工具 (使用PaddleOCR)")
    print("=" * 70)
    print(f"输入文件夹: {input_folder}")
    print(f"PaddleOCR处理后文件夹: {ocr_output_folder}")
    print(f"内容提取输出文件夹: {extract_output_folder}")
    
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
        print(f"进度: {i+1}/{len(pdf_files)}")
        try:
            processed_count += 1
            if process_single_pdf(pdf_file, ocr_output_folder, extract_output_folder):
                success_count += 1
        except Exception as e:
            print(f"处理文件 {pdf_file} 时发生错误: {str(e)}")
    
    print(f"\n处理完成!")
    print(f"总文件数: {len(pdf_files)}")
    print(f"已处理: {processed_count} 个文件")
    print(f"成功处理: {success_count} 个文件")
    print(f"PaddleOCR处理后文件目录: {ocr_output_folder}")
    print(f"内容提取输出目录: {extract_output_folder}")

if __name__ == "__main__":
    main()