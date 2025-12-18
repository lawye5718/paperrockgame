#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
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
        result = subprocess.run(command, capture_output=True, text=True, timeout=1800)  # 30分钟超时
        
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

def find_all_pdfs(root_folder, output_folder):
    """
    递归查找文件夹下的所有PDF文件，排除输出文件夹
    """
    pdf_files = []
    
    for root, dirs, files in os.walk(root_folder):
        # 跳过输出文件夹
        if os.path.abspath(root).startswith(os.path.abspath(output_folder)):
            continue
            
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    
    return pdf_files

def process_all_pdfs():
    """
    遍历输入文件夹及其子文件夹中的所有PDF文件，并使用OCRmyPDF进行处理
    """
    print("开始使用OCRmyPDF处理所有PDF文件")
    
    # 从环境变量获取配置
    input_folder = os.getenv('INPUT_PDF_FOLDER', '/Users/yuanliang/Downloads/testpdf')
    output_folder = os.getenv('OUTPUT_PDF_FOLDER', '/Users/yuanliang/Downloads/testpdf/OCRmyPDF处理结果')
    
    # 确保输出目录存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 查找要处理的PDF文件（包括子文件夹中的文件）
    pdf_files = find_all_pdfs(input_folder, output_folder)
    
    if not pdf_files:
        print(f"在 {input_folder} 目录及其子目录中未找到PDF文件")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf_file}")
    
    # 处理每个PDF文件
    successful_count = 0
    failed_count = 0
    
    for pdf_file in pdf_files:
        # 生成相对于输入文件夹的路径
        relative_path = os.path.relpath(pdf_file, input_folder)
        # 生成输出文件路径
        output_file = f"OCRmyPDF_{relative_path}"
        output_path = os.path.join(output_folder, output_file)
        
        # 确保输出文件的目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n开始处理: {relative_path}")
        success = ocrmypdf_process(pdf_file, output_path)
        
        if success:
            successful_count += 1
        else:
            failed_count += 1
    
    # 显示处理结果统计
    print(f"\n=== 处理完成 ===")
    print(f"成功处理: {successful_count} 个文件")
    print(f"处理失败: {failed_count} 个文件")
    print(f"总计处理: {len(pdf_files)} 个文件")
    print(f"输出文件保存在: {output_folder}")

def main():
    process_all_pdfs()

if __name__ == "__main__":
    main()