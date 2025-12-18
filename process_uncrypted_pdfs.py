#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

def process_pdf_with_ocrmypdf(input_path, output_path):
    """
    使用ocrmypdf处理单个PDF文件
    """
    try:
        # 构建ocrmypdf命令
        cmd = [
            'ocrmypdf',
            '-l', 'chi_sim',  # 简体中文
            '--optimize', '3',  # 最高级别压缩
            '--output-type', 'pdf',  # 输出标准PDF
            input_path,  # 输入文件
            output_path  # 输出文件
        ]
        
        print(f"正在处理: {input_path}")
        print(f"命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"成功处理: {os.path.basename(input_path)}")
            return True
        else:
            print(f"处理失败: {os.path.basename(input_path)}")
            print(f"错误信息: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"处理超时: {os.path.basename(input_path)}")
        return False
    except Exception as e:
        print(f"处理过程中发生错误: {os.path.basename(input_path)} - {str(e)}")
        return False

def find_pdf_files(directory):
    """
    查找目录中的所有PDF文件
    """
    pdf_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                pdf_files.append(full_path)
    
    return pdf_files

def main():
    # 定义输入和输出文件夹
    input_folder = "/Volumes/homes/yeweibing/北海案件资料/无密码盘"
    output_folder = "/Volumes/TU260Pro/北海案件资料_处理中/无密码文件"
    
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"输入文件夹: {input_folder}")
    print(f"输出文件夹: {output_folder}")
    
    # 查找所有PDF文件
    pdf_files = find_pdf_files(input_folder)
    
    print(f"\n找到 {len(pdf_files)} 个PDF文件需要处理")
    
    # 处理每个PDF文件
    processed_count = 0
    failed_count = 0
    
    for pdf_file in pdf_files:
        # 生成输出文件路径
        relative_path = os.path.relpath(pdf_file, input_folder)
        output_file = os.path.join(output_folder, relative_path)
        
        # 确保输出文件的目录存在
        output_dir = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        # 处理PDF文件
        if process_pdf_with_ocrmypdf(pdf_file, output_file):
            processed_count += 1
        else:
            failed_count += 1
    
    print(f"\n处理完成!")
    print(f"成功处理: {processed_count} 个文件")
    print(f"处理失败: {failed_count} 个文件")
    print(f"总计: {len(pdf_files)} 个文件")

if __name__ == "__main__":
    main()