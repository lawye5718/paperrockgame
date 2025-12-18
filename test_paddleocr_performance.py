#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz
from paddleocr import PaddleOCR
import os
import time
from PIL import Image

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

def test_paddleocr_single_page(pdf_path, page_number=0):
    """
    测试PaddleOCR处理PDF单页的性能
    """
    print(f"开始测试PaddleOCR处理PDF文件: {pdf_path}")
    print(f"测试页面: 第{page_number + 1}页")
    
    try:
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            print(f"错误: 文件不存在: {pdf_path}")
            return False
            
        # 打开PDF文件
        doc = fitz.open(pdf_path)
        
        if page_number >= len(doc):
            print(f"错误: PDF文件只有 {len(doc)} 页，无法访问第 {page_number + 1} 页")
            doc.close()
            return False
            
        # 获取指定页面
        page = doc[page_number]
        print(f"PDF总页数: {len(doc)}")
        
        # 记录开始时间
        start_time = time.time()
        
        # 将页面转换为图像 (使用更低DPI防止图片过大)
        print("正在将PDF页面转换为图像...")
        pix = page.get_pixmap(dpi=100)  # 进一步降低DPI到100
        
        # 保存临时图像文件
        temp_image_path = "temp_test_page.png"
        pix.save(temp_image_path)
        print(f"图像已保存到: {temp_image_path}")
        
        # 调整图片尺寸如果需要的话
        print("检查并调整图片尺寸...")
        temp_image_path = resize_image_if_needed(temp_image_path, max_size=2000)
        
        # 初始化PaddleOCR (简化参数以避免use_gpu错误)
        print("正在初始化PaddleOCR...")
        init_start = time.time()
        ocr = PaddleOCR(lang='ch')  # 简化参数，只保留必要的lang参数
        init_end = time.time()
        print(f"PaddleOCR初始化完成，耗时: {init_end - init_start:.2f}秒")
        
        # 对图像进行OCR
        print("正在进行OCR识别...")
        ocr_start = time.time()
        result = ocr.predict(temp_image_path)
        ocr_end = time.time()
        
        # 记录结束时间
        end_time = time.time()
        
        # 输出结果统计
        print(f"\n=== OCR处理结果 ===")
        print(f"总耗时: {end_time - start_time:.2f}秒")
        print(f"OCR识别耗时: {ocr_end - ocr_start:.2f}秒")
        
        if result and result[0]:
            rec_texts = result[0].get('rec_texts', [])
            print(f"识别到 {len(rec_texts)} 条文本")
            
            # 显示前几条识别结果
            print("\n前5条识别结果:")
            for i, text in enumerate(rec_texts[:5]):
                print(f"  {i+1}. {text}")
        else:
            print("未识别到文本")
        
        # 清理临时文件
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
            print(f"已删除临时文件: {temp_image_path}")
        
        doc.close()
        return True
        
    except Exception as e:
        print(f"PaddleOCR测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("PaddleOCR性能测试工具")
    print("=" * 50)
    
    # 测试文件路径（请根据实际情况修改）
    test_pdf_path = "/Volumes/TU260Pro/北海案件资料_处理中/原始卷/原始卷3/140移送卷（王雄昌）修改版_processed.pdf"
    
    # 测试第一页
    test_paddleocr_single_page(test_pdf_path, page_number=0)

if __name__ == "__main__":
    main()