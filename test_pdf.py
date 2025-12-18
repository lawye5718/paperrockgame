#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz
from paddleocr import PaddleOCR
import os

def main():
    print("正在测试PaddleOCR处理PDF文件...")
    
    try:
        # 初始化PaddleOCR，使用中文模型
        ocr = PaddleOCR(lang='ch')
        print("PaddleOCR初始化成功!")
        
        # 打开PDF文件
        pdf_path = '/Users/yuanliang/Downloads/乐清法律援助雷勇/法院卷1.pdf'
        if os.path.exists(pdf_path):
            print(f'PDF文件存在: {pdf_path}')
            doc = fitz.open(pdf_path)
            print(f'PDF页数: {len(doc)}')
            
            # 提取第一页
            page = doc[0]
            # 将页面转换为图像
            pix = page.get_pixmap(dpi=200)  # 提高DPI以获得更清晰的图像
            # 保存图像
            pix.save('page_0.png')
            print('已保存第一页为图像: page_0.png')
            
            # 对提取的图像进行OCR
            print('开始OCR识别...')
            result = ocr.predict('page_0.png')
            
            # 打印结果
            print('OCR识别完成，结果:')
            if result and result[0]:
                rec_texts = result[0].get('rec_texts', [])
                rec_scores = result[0].get('rec_scores', [])
                print(f"识别到{len(rec_texts)}条文本:")
                for i, (text, score) in enumerate(zip(rec_texts, rec_scores)):
                    print(f"  {i+1}. {text} (置信度: {score:.2f})")
            else:
                print("未识别到任何文本")
        else:
            print(f'PDF文件不存在: {pdf_path}')
            
    except Exception as e:
        print(f"PaddleOCR处理PDF失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()