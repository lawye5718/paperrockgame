#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz
from paddleocr import PaddleOCR
import os
import sys
from dotenv import load_dotenv
from PIL import Image
import cv2
import numpy as np

# 加载环境变量
load_dotenv()

def preprocess_image_for_ocr(image_path):
    """
    对图像进行预处理以提高OCR识别效果
    """
    try:
        # 读取图像
        img = cv2.imread(image_path)
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 应用高斯模糊以减少噪声
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # 应用阈值处理以增强对比度
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 保存预处理后的图像
        processed_path = image_path.replace('.png', '_processed.png')
        cv2.imwrite(processed_path, thresh)
        
        print(f"图像预处理完成，保存到: {processed_path}")
        return processed_path
    except Exception as e:
        print(f"图像预处理失败: {str(e)}")
        return image_path

def resize_image_if_needed(image_path, max_size=2000):
    """
    如果图片尺寸超过指定大小，则调整图片尺寸
    将最大尺寸减小到2000以避免内存问题
    """
    try:
        # 打开图片
        img = Image.open(image_path)
        width, height = img.size
        
        # 检查是否需要调整尺寸
        if width > max_size or height > max_size:
            # 计算缩放比例
            ratio = min(max_size/width, max_size/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # 调整图片尺寸
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存调整后的图片
            img.save(image_path)
            print(f"  图片尺寸已从 {width}x{height} 调整为 {new_width}x{new_height}")
        
        return image_path
    except Exception as e:
        print(f"调整图片尺寸时出错: {str(e)}")
        return image_path

def paddleocr_process_pdf_to_pdf(pdf_path, output_pdf_path):
    """
    使用PaddleOCR处理PDF文件，并生成带文本层的PDF文件
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        
        # 初始化PaddleOCR，使用中文模型 (根据测试代码中的配置)
        print("初始化PaddleOCR...")
        # 根据测试结果选择最佳配置
        ocr = PaddleOCR(lang='ch')  # 使用与测试代码相同的配置
        print("PaddleOCR初始化成功!")
        
        # 打开PDF文件
        if not os.path.exists(pdf_path):
            print(f'错误: PDF文件不存在: {pdf_path}')
            return False
            
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f'PDF页数: {total_pages}')
        
        # 为当前PDF创建唯一的OCR结果文件名前缀
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        pdf_dir_name = os.path.basename(os.path.dirname(pdf_path)) if os.path.dirname(pdf_path) else ""
        ocr_result_prefix = f"{pdf_dir_name}_{pdf_name}" if pdf_dir_name else pdf_name
        # 清理文件名中的特殊字符
        ocr_result_prefix = "".join(c for c in ocr_result_prefix if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        # 创建新的PDF文档用于保存结果
        output_doc = fitz.open()
        
        # 处理每一页
        for page_num in range(total_pages):
            print(f"正在处理第 {page_num + 1}/{total_pages} 页...")
            
            # 获取原始页面
            page = doc[page_num]
            
            # 将页面转换为图像 (提高DPI以改善OCR效果，但仍控制在合理范围内)
            pix = page.get_pixmap(dpi=200)  # 修改为200 DPI以提高OCR质量
            
            # 保存临时图像文件
            temp_image_path = f"temp_page_{page_num}.png"
            pix.save(temp_image_path)
            
            # 调整图片尺寸如果需要的话
            temp_image_path = resize_image_if_needed(temp_image_path, max_size=2000)
            
            # 预处理图像以提高OCR效果
            processed_image_path = preprocess_image_for_ocr(temp_image_path)
            
            # 调整处理后图像的尺寸
            processed_image_path = resize_image_if_needed(processed_image_path, max_size=2000)
            
            # 对图像进行OCR
            print(f"  正在对第 {page_num + 1} 页进行OCR识别...")
            result = ocr.predict(processed_image_path)
            
            # 中间存储OCR结果并输出到终端（使用唯一文件名避免覆盖）
            ocr_result_file = f"ocr_result_{ocr_result_prefix}_page_{page_num + 1}.txt"
            with open(ocr_result_file, 'w', encoding='utf-8') as f:
                f.write(f"OCR结果 - 第 {page_num + 1} 页\n")
                f.write("=" * 50 + "\n")
                f.write(f"处理的图像: {processed_image_path}\n")
                f.write(f"原始PDF页面: {page_num + 1}\n\n")
                
                if result and result[0]:
                    f.write("详细结果:\n")
                    f.write(str(result) + "\n\n")
                    
                    # 解析并格式化结果
                    texts = []
                    if isinstance(result[0], dict):
                        if 'rec_texts' in result[0]:
                            texts = result[0]['rec_texts']
                        elif 'text' in result[0]:
                            texts = [result[0]['text']]
                    elif isinstance(result[0], list):
                        for item in result[0]:
                            if isinstance(item, list) and len(item) > 1:
                                if isinstance(item[1], list) and len(item[1]) > 0:
                                    texts.append(str(item[1][0]))
                                elif isinstance(item[1], (str, int, float)):
                                    texts.append(str(item[1]))
                            elif isinstance(item, dict) and 'text' in item:
                                texts.append(item['text'])
                            elif isinstance(item, str):
                                texts.append(item)
                    
                    # 写入解析后的文本
                    f.write("解析后的文本:\n")
                    for i, text in enumerate(texts):
                        f.write(f"{i+1}. {text}\n")
                    
                    # 在终端输出结果摘要
                    print(f"    OCR结果摘要 - 第 {page_num + 1} 页:")
                    filtered_texts = [text for text in texts if text.strip() and not text.strip() in ['.', '。', ',', '，', ' ', '  ']]
                    if filtered_texts:
                        print(f"      识别到 {len(filtered_texts)} 条有效文本:")
                        for i, text in enumerate(filtered_texts[:5]):  # 显示前5条
                            print(f"        {i+1}. {text}")
                        if len(filtered_texts) > 5:
                            print(f"        ... 还有 {len(filtered_texts) - 5} 条文本")
                    else:
                        print("      未识别到有效文本")
                else:
                    f.write("未识别到任何文本\n")
                    print("    未识别到任何文本")
            
            print(f"    OCR结果已保存到: {ocr_result_file}")
            
            # 创建新页面并复制原始页面内容
            new_page = output_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.show_pdf_page(new_page.rect, doc, page_num)
            
            # 将OCR结果添加为文本层
            if result and result[0]:
                # 检查返回结果的格式
                texts = []
                boxes = []
                
                # 解析不同格式的OCR结果
                if isinstance(result[0], dict):
                    # 新格式
                    if 'rec_texts' in result[0]:
                        texts = result[0]['rec_texts']
                        boxes = result[0].get('rec_boxes', [])
                    elif 'text' in result[0]:
                        texts = [result[0]['text']]
                elif isinstance(result[0], list):
                    # 旧格式或其他格式，尝试解析
                    for item in result[0]:
                        if isinstance(item, dict) and 'text' in item:
                            texts.append(item['text'])
                            if 'box' in item:
                                boxes.append(item['box'])
                        elif isinstance(item, list) and len(item) >= 2:
                            # 格式: [box, (text, confidence)]
                            if isinstance(item[1], list) and len(item[1]) >= 2:
                                texts.append(str(item[1][0]))
                            elif isinstance(item[1], (str, int, float)):
                                texts.append(str(item[1]))
                            
                            # 如果第一个元素是坐标框
                            if len(item) > 0 and isinstance(item[0], (list, tuple)):
                                boxes.append(item[0])
                
                # 在页面上添加透明文本
                for i, text in enumerate(texts):
                    if text.strip():
                        try:
                            # 尝试使用坐标框放置文本（如果可用）
                            if i < len(boxes) and boxes[i] is not None:
                                # 验证boxes[i]的结构
                                box = boxes[i]
                                if isinstance(box, (list, tuple)) and len(box) >= 4:
                                    # 计算文本框坐标
                                    x_coords = [point[0] for point in box] if isinstance(box[0], (list, tuple)) else box[::2]
                                    y_coords = [point[1] for point in box] if isinstance(box[0], (list, tuple)) else box[1::2]
                                    
                                    x0, y0 = min(x_coords), min(y_coords)
                                    x1, y1 = max(x_coords), max(y_coords)
                                    
                                    # 创建文本矩形区域
                                    rect = fitz.Rect(x0, y0, x1, y1)
                                    
                                    # 插入文本
                                    new_page.insert_textbox(
                                        rect, 
                                        text,
                                        fontsize=1,
                                        color=(0, 0, 0),
                                        overlay=True
                                    )
                                else:
                                    # 如果坐标框格式不正确，使用默认位置
                                    new_page.insert_text(
                                        (10, 10 + i*12),
                                        text,
                                        fontsize=1,
                                        color=(0, 0, 0),
                                        overlay=True
                                    )
                            else:
                                # 没有坐标信息，使用默认位置
                                new_page.insert_text(
                                    (10, 10 + i*12),
                                    text,
                                    fontsize=1,
                                    color=(0, 0, 0),
                                    overlay=True
                                )
                        except Exception as e:
                            # 如果插入文本失败，跳过该项
                            print(f"    插入文本时出错: {str(e)}")
                            pass
            
            # 删除临时图像文件
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            if os.path.exists(processed_image_path) and processed_image_path != temp_image_path:
                os.remove(processed_image_path)
            print(f"  第 {page_num + 1} 页处理完成")
        
        # 保存处理后的PDF
        output_doc.save(output_pdf_path)
        output_doc.close()
        doc.close()
        
        print(f"PDF处理完成，结果已保存到: {output_pdf_path}")
        return True
        
    except Exception as e:
        print(f"PaddleOCR处理PDF失败: {str(e)}")
        import traceback
        traceback.print_exc()
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
        
        # 保存文字到MD文件（根据要求修改命名方式）
        md_filename = f"{pdf_name}{page_type}.md"  # 移除了"_"分隔符
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
        if not paddleocr_process_pdf_to_pdf(pdf_path, ocr_pdf_path):
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
    print("北海案件PDF文档PaddleOCR处理工具")
    
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
    
    # 确保输出目录存在
    os.makedirs(ocr_output_folder, exist_ok=True)
    os.makedirs(extract_output_folder, exist_ok=True)
    
    # 查找要处理的PDF文件
    pdf_files = []
    if os.path.exists(input_folder):
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file.lower().endswith('.pdf') and not file.startswith('._'):
                    full_path = os.path.join(root, file)
                    pdf_files.append(full_path)
    
    if not pdf_files:
        print(f"在 {input_folder} 目录中未找到PDF文件")
        return
    
    print(f"\n找到 {len(pdf_files)} 个PDF文件")
    
    # 处理每个PDF文件
    success_count = 0
    for i, pdf_file in enumerate(pdf_files):
        print(f"\n进度: {i+1}/{len(pdf_files)}")
        print(f"开始处理: {pdf_file}")
        
        success = process_single_pdf(pdf_file, ocr_output_folder, extract_output_folder)
        
        if success:
            success_count += 1
            print(f"成功处理: {pdf_file}")
        else:
            print(f"处理失败: {pdf_file}")
    
    print(f"\n处理完成!")
    print(f"总文件数: {len(pdf_files)}")
    print(f"成功处理: {success_count} 个文件")
    print(f"PaddleOCR处理后文件目录: {ocr_output_folder}")
    print(f"内容提取输出目录: {extract_output_folder}")

if __name__ == "__main__":
    main()