#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz
from paddleocr import PaddleOCR
import os
from PIL import Image

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

def test_cover_ocr_high_dpi(pdf_path):
    """
    测试使用更高DPI进行OCR识别
    """
    print(f"开始测试PDF封面OCR (高DPI): {pdf_path}")
    
    try:
        # 打开PDF文件
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            print("PDF文件没有页面")
            return False
            
        # 获取第一页（封面）
        page = doc[0]
        print(f"PDF总页数: {len(doc)}")
        
        # 尝试不同的DPI设置
        dpi_settings = [150, 200, 300]
        
        for dpi in dpi_settings:
            print(f"\n测试 DPI: {dpi}")
            
            # 将封面转换为图像
            print(f"正在将封面转换为图像 (DPI: {dpi})...")
            pix = page.get_pixmap(dpi=dpi)
            
            # 保存图像
            image_path = f"cover_dpi_{dpi}.png"
            pix.save(image_path)
            print(f"封面图像已保存到: {image_path}")
            
            # 调整图像尺寸以避免过大
            image_path = resize_image_if_needed(image_path, max_size=2000)
            
            # 初始化PaddleOCR
            print("初始化PaddleOCR...")
            ocr = PaddleOCR(lang='ch')
            
            # 进行OCR识别
            print("正在进行OCR识别...")
            result = ocr.predict(image_path)
            
            # 显示结果
            print_result(result, dpi)
            
            # 清理临时文件
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # 关闭PDF文档
        doc.close()
        
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def print_result(result, dpi):
    """
    打印OCR结果
    """
    print(f"\n--- DPI {dpi} 的OCR结果 ---")
    
    if not result or not result[0]:
        print("未识别到任何文本")
        return
    
    # 解析结果
    try:
        if 'rec_texts' in result[0]:
            # 新格式
            texts = result[0]['rec_texts']
        else:
            # 旧格式
            texts = []
            for item in result[0]:
                if isinstance(item, list) and len(item) > 1:
                    if isinstance(item[1], list) and len(item[1]) > 0:
                        texts.append(str(item[1][0]))
                    else:
                        texts.append(str(item[1]))
                elif isinstance(item, dict) and 'text' in item:
                    texts.append(item['text'])
                    
        # 过滤有效文本
        valid_texts = [text for text in texts if text.strip() and len(text.strip()) > 1]
        
        if valid_texts:
            print(f"识别到 {len(valid_texts)} 条有效文本:")
            for i, text in enumerate(valid_texts[:10]):  # 显示前10条
                print(f"  {i+1}. {text}")
            if len(valid_texts) > 10:
                print(f"  ... 还有 {len(valid_texts) - 10} 条文本")
        else:
            print("未识别到有效文本")
            
    except Exception as e:
        print(f"解析结果时出错: {str(e)}")

def main():
    print("PDF封面高DPI OCR测试工具")
    print("=" * 40)
    
    # 测试文件路径
    test_pdf_path = "/Volumes/TU260Pro/北海案件资料_处理中/原始卷/原始卷3/140移送卷（王雄昌）修改版_processed.pdf"
    
    # 测试封面OCR
    test_cover_ocr_high_dpi(test_pdf_path)

if __name__ == "__main__":
    main()