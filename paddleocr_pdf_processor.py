#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz
from paddleocr import PaddleOCR
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def paddleocr_process_pdf(pdf_path, output_folder):
    """
    使用PaddleOCR处理PDF文件，将每页转换为图像并进行OCR识别，
    最后将结果保存为Markdown文件
    """
    try:
        # 确保输出文件夹存在
        os.makedirs(output_folder, exist_ok=True)
        
        # 获取PDF文件名（不含扩展名）
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # 初始化PaddleOCR，使用中英文模型
        print("初始化PaddleOCR...")
        ocr = PaddleOCR(lang='ch', use_textline_orientation=True)
        print("PaddleOCR初始化成功!")
        
        # 打开PDF文件
        if not os.path.exists(pdf_path):
            print(f'错误: PDF文件不存在: {pdf_path}')
            return False
            
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f'PDF页数: {total_pages}')
        
        # 创建Markdown文件
        md_file_path = os.path.join(output_folder, f"{pdf_name}.md")
        
        with open(md_file_path, 'w', encoding='utf-8') as md_file:
            md_file.write(f"# {pdf_name}\n\n")
            
            # 处理每一页
            for page_num in range(total_pages):
                print(f"正在处理第 {page_num + 1}/{total_pages} 页...")
                
                # 提取页面
                page = doc[page_num]
                
                # 将页面转换为图像
                pix = page.get_pixmap(dpi=200)  # 使用200 DPI以平衡质量和处理速度
                
                # 保存图像
                image_filename = f"{pdf_name}_page_{page_num + 1}.png"
                image_path = os.path.join(output_folder, image_filename)
                pix.save(image_path)
                
                # 在Markdown中添加页面标题
                md_file.write(f"## 第{page_num + 1}页\n\n")
                md_file.write(f"![第{page_num + 1}页]({image_filename})\n\n")
                
                # 对图像进行OCR
                print(f"  正在对第 {page_num + 1} 页进行OCR识别...")
                result = ocr.predict(image_path)
                
                # 解析OCR结果并写入Markdown
                if result and result[0]:
                    rec_texts = result[0].get('rec_texts', [])
                    if rec_texts:
                        md_file.write("### OCR识别结果:\n\n")
                        for text in rec_texts:
                            # 过滤掉置信度极低的识别结果
                            if text.strip():  # 只有非空文本才写入
                                md_file.write(f"{text}\n\n")
                    else:
                        md_file.write("OCR识别结果: 未识别到文本\n\n")
                else:
                    md_file.write("OCR识别结果: 未识别到文本\n\n")
                
                md_file.write("---\n\n")  # 页面分隔线
                
                print(f"  第 {page_num + 1} 页处理完成")
        
        print(f"PDF处理完成，结果已保存到: {md_file_path}")
        return True
        
    except Exception as e:
        print(f"PaddleOCR处理PDF失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("PaddleOCR PDF处理工具")
    
    # 从环境变量获取配置
    input_folder = os.getenv('INPUT_PDF_FOLDER', '/Users/yuanliang/Downloads/乐清法律援助雷勇')
    output_folder = os.getenv('OUTPUT_PDF_FOLDER', '/Users/yuanliang/Downloads/乐清法律援助雷勇/OCR结果')
    
    # 确保输出目录存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 查找要处理的PDF文件
    pdf_files = []
    if os.path.exists(input_folder):
        for file in os.listdir(input_folder):
            if file.lower().endswith('.pdf'):
                pdf_files.append(file)
    
    if not pdf_files:
        print(f"在 {input_folder} 目录中未找到PDF文件")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf_file}")
    
    # 处理每个PDF文件
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_folder, pdf_file)
        print(f"\n开始处理: {pdf_file}")
        
        # 为每个PDF创建单独的输出文件夹
        pdf_output_folder = os.path.join(output_folder, os.path.splitext(pdf_file)[0])
        success = paddleocr_process_pdf(pdf_path, pdf_output_folder)
        
        if success:
            print(f"成功处理: {pdf_file}")
        else:
            print(f"处理失败: {pdf_file}")

if __name__ == "__main__":
    main()