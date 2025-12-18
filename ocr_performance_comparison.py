#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz
from paddleocr import PaddleOCR
import os
import sys
import time
import subprocess
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def ocrmypdf_process(input_path, output_path):
    """
    使用OCRmyPDF处理PDF文件
    """
    try:
        # 构建OCRmyPDF命令
        command = [
            'ocrmypdf',
            '-l', 'chi_sim+eng',
            '--optimize', '3',
            '--skip-text',  # 跳过已有文本的页面
            '--clean',      # 清理优化
            '--output-type', 'pdf',
            input_path,
            output_path
        ]
        
        print(f"使用OCRmyPDF处理: {os.path.basename(input_path)}")
        start_time = time.time()
        result = subprocess.run(command, capture_output=True, text=True, timeout=1800)  # 30分钟超时
        end_time = time.time()
        
        if result.returncode == 0:
            print(f"OCRmyPDF处理成功: {os.path.basename(input_path)} (耗时: {end_time - start_time:.2f}秒)")
            return True, end_time - start_time
        else:
            print(f"OCRmyPDF处理失败: {os.path.basename(input_path)}")
            print(f"错误信息: {result.stderr}")
            return False, 0
    except subprocess.TimeoutExpired:
        print(f"OCRmyPDF处理超时: {os.path.basename(input_path)}")
        return False, 0
    except Exception as e:
        print(f"OCRmyPDF处理出错: {os.path.basename(input_path)} - {str(e)}")
        return False, 0

def paddleocr_process_pdf(pdf_path, output_folder):
    """
    使用PaddleOCR处理PDF文件，将每页转换为图像并进行OCR识别，
    最后将结果保存为Markdown文件
    """
    start_time = time.time()
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
            return False, 0
            
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f'PDF页数: {total_pages}')
        
        # 创建Markdown文件
        md_file_path = os.path.join(output_folder, f"{pdf_name}_paddle.md")
        
        with open(md_file_path, 'w', encoding='utf-8') as md_file:
            md_file.write(f"# {pdf_name} (PaddleOCR处理结果)\n\n")
            
            # 处理每一页
            for page_num in range(total_pages):
                page_start_time = time.time()
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
                
                # 计算当前页处理时间
                page_end_time = time.time()
                page_time = page_end_time - page_start_time
                
                # 估算总时间
                elapsed_time = page_end_time - start_time
                estimated_total_time = elapsed_time / (page_num + 1) * total_pages
                remaining_time = estimated_total_time - elapsed_time
                
                print(f"  第 {page_num + 1} 页处理完成 (耗时: {page_time:.2f}秒)")
                print(f"  累计用时: {elapsed_time:.2f}秒, 预计总用时: {estimated_total_time:.2f}秒, 剩余时间: {remaining_time:.2f}秒")
        
        end_time = time.time()
        total_time = end_time - start_time
        print(f"PaddleOCR处理完成，结果已保存到: {md_file_path} (总耗时: {total_time:.2f}秒)")
        return True, total_time
        
    except Exception as e:
        end_time = time.time()
        print(f"PaddleOCR处理PDF失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, end_time - start_time

def compare_ocr_performance():
    """
    比较OCRmyPDF和PaddleOCR的性能
    """
    print("开始比较OCRmyPDF和PaddleOCR的性能")
    
    # 从环境变量获取配置
    input_folder = os.getenv('INPUT_PDF_FOLDER', '/Users/yuanliang/Downloads/testpdf')
    output_folder = os.getenv('OUTPUT_PDF_FOLDER', '/Users/yuanliang/Downloads/testpdf')
    
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
    
    # 性能比较结果
    performance_results = []
    
    # 处理每个PDF文件
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_folder, pdf_file)
        print(f"\n开始处理: {pdf_file}")
        
        # 1. 使用OCRmyPDF处理
        ocrmypdf_output = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}_ocrmypdf.pdf")
        print(f"\n--- 使用OCRmyPDF处理 {pdf_file} ---")
        ocrmypdf_success, ocrmypdf_time = ocrmypdf_process(pdf_path, ocrmypdf_output)
        
        # 2. 使用PaddleOCR处理
        paddle_output_folder = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}_paddle")
        print(f"\n--- 使用PaddleOCR处理 {pdf_file} ---")
        paddle_success, paddle_time = paddleocr_process_pdf(pdf_path, paddle_output_folder)
        
        # 记录结果
        result = {
            'file': pdf_file,
            'ocrmypdf_success': ocrmypdf_success,
            'ocrmypdf_time': ocrmypdf_time if ocrmypdf_success else None,
            'paddle_success': paddle_success,
            'paddle_time': paddle_time if paddle_success else None
        }
        performance_results.append(result)
        
        # 显示单个文件的比较结果
        if ocrmypdf_success and paddle_success:
            time_ratio = paddle_time / ocrmypdf_time
            print(f"\n=== {pdf_file} 性能比较 ===")
            print(f"OCRmyPDF耗时: {ocrmypdf_time:.2f}秒")
            print(f"PaddleOCR耗时: {paddle_time:.2f}秒")
            print(f"时间比率 (PaddleOCR/OCRmyPDF): {time_ratio:.2f}")
            if time_ratio > 1:
                print(f"PaddleOCR比OCRmyPDF慢 {time_ratio:.2f} 倍")
            else:
                print(f"PaddleOCR比OCRmyPDF快 {1/time_ratio:.2f} 倍")
    
    # 显示总体比较结果
    print(f"\n=== 总体性能比较 ===")
    total_ocrmypdf_time = 0
    total_paddle_time = 0
    successful_comparisons = 0
    
    for result in performance_results:
        if result['ocrmypdf_success'] and result['paddle_success']:
            total_ocrmypdf_time += result['ocrmypdf_time']
            total_paddle_time += result['paddle_time']
            successful_comparisons += 1
            print(f"{result['file']}: OCRmyPDF {result['ocrmypdf_time']:.2f}秒 vs PaddleOCR {result['paddle_time']:.2f}秒")
    
    if successful_comparisons > 0:
        avg_ocrmypdf_time = total_ocrmypdf_time / successful_comparisons
        avg_paddle_time = total_paddle_time / successful_comparisons
        avg_ratio = avg_paddle_time / avg_ocrmypdf_time
        
        print(f"\n平均性能比较:")
        print(f"OCRmyPDF平均耗时: {avg_ocrmypdf_time:.2f}秒")
        print(f"PaddleOCR平均耗时: {avg_paddle_time:.2f}秒")
        print(f"平均时间比率 (PaddleOCR/OCRmyPDF): {avg_ratio:.2f}")
        if avg_ratio > 1:
            print(f"PaddleOCR平均比OCRmyPDF慢 {avg_ratio:.2f} 倍")
        else:
            print(f"PaddleOCR平均比OCRmyPDF快 {1/avg_ratio:.2f} 倍")

def main():
    compare_ocr_performance()

if __name__ == "__main__":
    main()