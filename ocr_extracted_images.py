#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import fitz  # PyMuPDF
import pandas as pd
from pathlib import Path
import subprocess
import tempfile

def extract_text_from_image_with_ocrmypdf(image_path):
    """
    使用OCRmyPDF处理单张图片并提取文本
    """
    try:
        # 创建临时PDF文件
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            tmp_pdf_path = tmp_pdf.name
        
        # 使用OCRmyPDF将图片转换为带OCR文本的PDF
        cmd = [
            'ocrmypdf',
            '-l', 'chi_sim',  # 简体中文
            '--output-type', 'pdf',
            '--force-ocr',  # 强制OCR
            image_path,
            tmp_pdf_path
        ]
        
        # 执行OCRmyPDF
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # 2分钟超时
        
        if result.returncode == 0:
            # 从生成的PDF中提取文本
            doc = fitz.open(tmp_pdf_path)
            text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
            doc.close()
            
            # 删除临时文件
            os.unlink(tmp_pdf_path)
            
            return text.strip()
        else:
            print(f"OCR处理失败: {image_path}")
            print(f"错误信息: {result.stderr}")
            # 删除临时文件
            if os.path.exists(tmp_pdf_path):
                os.unlink(tmp_pdf_path)
            return ""
            
    except subprocess.TimeoutExpired:
        print(f"OCR处理超时: {image_path}")
        return ""
    except Exception as e:
        print(f"OCR处理出错: {str(e)}")
        return ""

def find_images_in_directory(base_dir):
    """
    在指定目录中查找所有图片文件
    返回一个字典，键为父文件夹名称，值为该文件夹中的图片文件列表
    """
    folder_images = {}
    
    # 遍历所有子目录
    for root, dirs, files in os.walk(base_dir):
        # 获取当前目录的父文件夹名称
        parent_folder = os.path.basename(root)
        
        # 查找图片文件
        image_files = []
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                image_files.append(os.path.join(root, file))
        
        # 如果找到了图片文件，则记录
        if image_files:
            # 获取父文件夹的父文件夹名称作为标识
            grandparent_folder = os.path.basename(os.path.dirname(root))
            key = f"{grandparent_folder}/{parent_folder}"
            folder_images[key] = sorted(image_files)
    
    return folder_images

def main():
    # 定义输入和输出文件夹
    input_folder = "/Users/yuanliang/Downloads/beihai_extracted"
    output_file = "/Users/yuanliang/Downloads/ocr_results.xlsx"
    
    print("=" * 60)
    print("图片OCR识别及表格生成工具 (使用OCRmyPDF)")
    print("=" * 60)
    print(f"输入文件夹: {input_folder}")
    print(f"输出文件: {output_file}")
    
    # 查找所有图片文件
    print("正在查找图片文件...")
    folder_images = find_images_in_directory(input_folder)
    print(f"找到 {len(folder_images)} 个包含图片的文件夹")
    
    # 准备数据
    data = []
    index = 1
    
    # 处理每个文件夹中的图片
    for folder_name, image_files in folder_images.items():
        print(f"正在处理文件夹: {folder_name} ({len(image_files)} 张图片)")
        
        # 处理第一张图片
        first_image_text = ""
        if len(image_files) > 0:
            first_image_text = extract_text_from_image_with_ocrmypdf(image_files[0])
            print(f"  第一张图片OCR完成")
        
        # 处理第二张及以后的图片
        other_images_text = ""
        for i in range(1, len(image_files)):
            image_text = extract_text_from_image_with_ocrmypdf(image_files[i])
            other_images_text += f"[图片{i+1}]\n{image_text}\n\n"
        
        # 添加到数据列表
        data.append({
            '序号': index,
            '文件夹名称': folder_name,
            '第一张图片内容': first_image_text,
            '其他图片内容': other_images_text.strip()
        })
        
        index += 1
    
    # 创建DataFrame并保存到Excel
    if data:
        df = pd.DataFrame(data)
        df.to_excel(output_file, index=False)
        print(f"\n处理完成! 结果已保存到: {output_file}")
        print(f"共处理 {len(data)} 个文件夹")
    else:
        print("未找到任何图片文件进行处理")

if __name__ == "__main__":
    main()