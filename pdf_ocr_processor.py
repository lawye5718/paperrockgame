#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz
from paddleocr import PaddleOCR
import os
import subprocess

def ocrmypdf_ocr(input_path, output_path):
    """
    使用OCRmyPDF进行OCR处理
    """
    try:
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
        
        print(f"使用OCRmyPDF处理: {input_path}")
        result = subprocess.run(command, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"OCRmyPDF处理成功: {os.path.basename(input_path)}")
            return True
        else:
            print(f"OCRmyPDF处理失败: {os.path.basename(input_path)}")
            print(f"错误信息: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"OCRmyPDF处理超时: {os.path.basename(input_path)}")
        return False
    except Exception as e:
        print(f"OCRmyPDF处理出错: {os.path.basename(input_path)} - {str(e)}")
        return False

def paddleocr_ocr(pdf_path):
    """
    使用PaddleOCR进行OCR处理（备选方案）
    """
    try:
        # 初始化PaddleOCR，使用中文模型
        ocr = PaddleOCR(lang='ch')
        print("PaddleOCR初始化成功!")
        
        if os.path.exists(pdf_path):
            print(f'PDF文件存在: {pdf_path}')
            doc = fitz.open(pdf_path)
            print(f'PDF页数: {len(doc)}')
            
            # 提取第一页作为测试
            page = doc[0]
            # 将页面转换为图像
            pix = page.get_pixmap(dpi=200)  # 提高DPI以获得更清晰的图像
            # 保存图像
            image_path = 'temp_page.png'
            pix.save(image_path)
            print('已保存第一页为图像')
            
            # 对提取的图像进行OCR
            print('开始OCR识别...')
            result = ocr.predict(image_path)
            
            # 打印结果
            print('OCR识别完成')
            if result and result[0]:
                rec_texts = result[0].get('rec_texts', [])
                rec_scores = result[0].get('rec_scores', [])
                print(f"识别到{len(rec_texts)}条文本:")
                for i, (text, score) in enumerate(zip(rec_texts, rec_scores)):
                    print(f"  {i+1}. {text} (置信度: {score:.2f})")
                return rec_texts
            else:
                print("未识别到任何文本")
                return []
        else:
            print(f'PDF文件不存在: {pdf_path}')
            return []
    except Exception as e:
        print(f"PaddleOCR处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("PDF OCR处理工具")
    print("1. 首先尝试使用OCRmyPDF")
    print("2. 如果OCRmyPDF不可用，则使用PaddleOCR作为备选方案")
    
    # PDF文件路径
    pdf_path = '/Users/yuanliang/Downloads/乐清法律援助雷勇/法院卷1.pdf'
    output_path = '/Users/yuanliang/Downloads/乐清法律援助雷勇/法院卷1_优化版.pdf'
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 首先尝试使用OCRmyPDF
    success = ocrmypdf_ocr(pdf_path, output_path)
    
    if not success:
        print("OCRmyPDF处理失败，尝试使用PaddleOCR...")
        # 如果OCRmyPDF失败，使用PaddleOCR作为备选方案
        texts = paddleocr_ocr(pdf_path)
        if texts:
            print("PaddleOCR处理成功")
        else:
            print("PaddleOCR处理也失败了")

if __name__ == "__main__":
    main()