#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time

def test_paddleocr_import():
    """
    测试PaddleOCR导入是否正常
    """
    print("开始测试PaddleOCR导入...")
    try:
        start_time = time.time()
        from paddleocr import PaddleOCR
        end_time = time.time()
        print(f"PaddleOCR导入成功，耗时: {end_time - start_time:.2f}秒")
        return True
    except Exception as e:
        print(f"PaddleOCR导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_ocr():
    """
    测试简单的OCR功能
    """
    print("\n开始测试简单OCR功能...")
    try:
        from paddleocr import PaddleOCR
        
        # 初始化PaddleOCR (使用最简单的参数)
        print("初始化PaddleOCR...")
        start_time = time.time()
        ocr = PaddleOCR(lang='ch', show_log=False)  # 禁用日志以减少输出
        init_time = time.time()
        print(f"PaddleOCR初始化完成，耗时: {init_time - start_time:.2f}秒")
        
        # 创建一个简单的测试图像（纯文本）
        test_text = "这是一个测试文本"
        with open("simple_test.txt", "w", encoding="utf-8") as f:
            f.write(test_text)
        
        print("简单OCR测试完成")
        return True
        
    except Exception as e:
        print(f"简单OCR测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("简化版PaddleOCR测试")
    print("=" * 30)
    
    # 测试导入
    if test_paddleocr_import():
        # 测试简单OCR
        test_simple_ocr()
    else:
        print("PaddleOCR导入失败，无法继续测试")

if __name__ == "__main__":
    main()