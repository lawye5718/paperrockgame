#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from paddleocr import PaddleOCR
import os

def test_ocr_on_existing_images():
    """
    测试OCR在已存在的图像上的效果
    """
    print("开始测试OCR在已存在图像上的效果")
    
    # 测试图像列表
    test_images = [
        "cover_original.png",
        "cover_original_processed.png",
        "page_0.png"
    ]
    
    # 检查哪些图像文件存在
    existing_images = [img for img in test_images if os.path.exists(img)]
    
    if not existing_images:
        print("未找到任何测试图像文件")
        return
    
    print(f"找到以下图像文件: {existing_images}")
    
    # 初始化PaddleOCR
    print("初始化PaddleOCR...")
    ocr = PaddleOCR(lang='ch')
    print("PaddleOCR初始化完成")
    
    # 测试每个图像
    for image_path in existing_images:
        print(f"\n{'='*50}")
        print(f"测试图像: {image_path}")
        print(f"文件大小: {os.path.getsize(image_path) / 1024:.1f} KB")
        
        try:
            # 进行OCR识别
            print("正在进行OCR识别...")
            result = ocr.predict(image_path)
            
            # 显示结果
            print_result(result, image_path)
            
        except Exception as e:
            print(f"处理图像 {image_path} 时出错: {str(e)}")
            import traceback
            traceback.print_exc()

def print_result(result, image_name):
    """
    打印OCR结果
    """
    print(f"\n--- {image_name} 的OCR结果 ---")
    
    if not result or not result[0]:
        print("未识别到任何文本")
        return
    
    # 解析结果
    try:
        texts = []
        if isinstance(result[0], dict) and 'rec_texts' in result[0]:
            # 新格式
            texts = result[0]['rec_texts']
        elif isinstance(result[0], list):
            # 旧格式
            for item in result[0]:
                if isinstance(item, list) and len(item) > 1:
                    if isinstance(item[1], list) and len(item[1]) > 0:
                        texts.append(str(item[1][0]))
                    else:
                        texts.append(str(item[1]))
                elif isinstance(item, dict) and 'text' in item:
                    texts.append(item['text'])
                elif isinstance(item, str):
                    texts.append(item)
                    
        # 过滤有效文本
        valid_texts = [text for text in texts if text.strip() and len(text.strip()) > 1]
        
        if valid_texts:
            print(f"识别到 {len(valid_texts)} 条有效文本:")
            for i, text in enumerate(valid_texts[:15]):  # 显示前15条
                print(f"  {i+1}. {text}")
            if len(valid_texts) > 15:
                print(f"  ... 还有 {len(valid_texts) - 15} 条文本")
        else:
            print("未识别到有效文本")
            # 显示所有识别结果用于调试
            print("所有识别结果:")
            for i, item in enumerate(result[0][:10] if isinstance(result[0], list) else []):
                print(f"  {i+1}. {item}")
                
    except Exception as e:
        print(f"解析结果时出错: {str(e)}")

def main():
    print("现有图像OCR测试工具")
    print("=" * 40)
    
    # 测试OCR
    test_ocr_on_existing_images()

if __name__ == "__main__":
    main()