#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz
from paddleocr import PaddleOCR
import os
from PIL import Image
import cv2
import numpy as np

def resize_image_if_needed(image_path, max_size=2000):
    """
    如果图片尺寸超过指定大小，则调整图片尺寸
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

def test_cover_ocr(pdf_path, dpi=150):
    """
    测试PDF封面的OCR识别效果
    """
    print(f"开始测试PDF封面OCR: {pdf_path}")
    
    try:
        # 打开PDF文件
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            print("PDF文件没有页面")
            return False
            
        # 获取第一页（封面）
        page = doc[0]
        print(f"PDF总页数: {len(doc)}")
        
        # 将封面转换为图像 (使用较低DPI以避免图像过大)
        print(f"正在将封面转换为图像 (DPI: {dpi})...")
        pix = page.get_pixmap(dpi=dpi)
        
        # 保存原始图像
        original_image_path = "cover_original.png"
        pix.save(original_image_path)
        print(f"原始封面图像已保存到: {original_image_path}")
        
        # 调整图像尺寸以避免过大
        original_image_path = resize_image_if_needed(original_image_path, max_size=2000)
        
        # 预处理图像
        processed_image_path = preprocess_image_for_ocr(original_image_path)
        
        # 调整处理后图像的尺寸
        processed_image_path = resize_image_if_needed(processed_image_path, max_size=2000)
        
        # 测试不同的PaddleOCR配置
        print("\n测试不同的PaddleOCR配置:")
        
        # 配置1: 简化参数
        print("\n1. 使用简化参数...")
        ocr1 = PaddleOCR(lang='ch')
        result1 = ocr1.predict(processed_image_path)
        print_result(result1, "简化参数")
        
        # 配置2: 启用角度检测
        print("\n2. 启用角度检测...")
        ocr2 = PaddleOCR(lang='ch', use_angle_cls=True)
        result2 = ocr2.predict(processed_image_path)
        print_result(result2, "角度检测")
        
        # 配置3: 使用不同的后处理参数
        print("\n3. 使用不同的后处理参数...")
        ocr3 = PaddleOCR(lang='ch')
        result3 = ocr3.predict(original_image_path)  # 使用原始图像
        print_result(result3, "原始图像")
        
        # 关闭PDF文档
        doc.close()
        
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def print_result(result, config_name):
    """
    打印OCR结果
    """
    print(f"\n--- {config_name} 结果 ---")
    
    if not result or not result[0]:
        print("未识别到任何文本")
        return
    
    # 尝试不同的结果格式
    texts = []
    try:
        # 检查是否是新格式
        if isinstance(result[0], dict):
            if 'rec_texts' in result[0]:
                texts = result[0]['rec_texts']
            elif 'text' in result[0]:
                texts = [result[0]['text']]
        # 检查是否是旧格式
        elif isinstance(result[0], list):
            for item in result[0]:
                if isinstance(item, list) and len(item) > 1:
                    if isinstance(item[1], list) and len(item[1]) > 0:
                        texts.append(str(item[1][0]))
                    elif isinstance(item[1], (str, int, float)):
                        texts.append(str(item[1]))
                elif isinstance(item, dict) and 'text' in item:
                    texts.append(item['text'])
                elif isinstance(item, dict) and 'rec_text' in item:
                    texts.append(item['rec_text'])
                elif isinstance(item, str):
                    texts.append(item)
    except Exception as e:
        print(f"解析结果时出错: {str(e)}")
    
    if texts:
        # 过滤掉空文本和纯标点符号文本
        filtered_texts = [text for text in texts if text.strip() and not text.strip() in ['.', '。', ',', '，', ' ', '  ']]
        
        if filtered_texts:
            print(f"识别到 {len(filtered_texts)} 条有效文本:")
            for i, text in enumerate(filtered_texts[:15]):  # 显示前15条
                print(f"  {i+1}. {text}")
            if len(filtered_texts) > 15:
                print(f"  ... 还有 {len(filtered_texts) - 15} 条文本")
        else:
            print("未识别到有效文本")
    else:
        print("无法解析识别结果或未识别到文本")

def main():
    print("PDF封面OCR测试工具")
    print("=" * 40)
    
    # 测试文件路径
    test_pdf_path = "/Volumes/TU260Pro/北海案件资料_处理中/原始卷/原始卷3/140移送卷（王雄昌）修改版_processed.pdf"
    
    # 测试封面OCR
    test_cover_ocr(test_pdf_path)

if __name__ == "__main__":
    main()