#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil

def get_pdf_files(directory):
    """
    获取目录中的所有PDF文件
    """
    pdf_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                pdf_files.append((file, full_path, relative_path))
    
    return pdf_files

def main():
    # 定义文件夹路径
    source_folder = "/Volumes/homes/yeweibing/北海案件资料/无密码盘"
    processed_folder = "/Volumes/TU260Pro/北海案件资料_处理中/无密码文件"
    failed_folder = "/Volumes/TU260Pro/北海案件资料_处理中/处理失败无密码文件"
    
    # 确保目标文件夹存在
    os.makedirs(failed_folder, exist_ok=True)
    
    print(f"源文件夹: {source_folder}")
    print(f"已处理文件夹: {processed_folder}")
    print(f"失败文件夹: {failed_folder}")
    
    # 获取所有源文件
    source_files = get_pdf_files(source_folder)
    print(f"\n源文件夹中找到 {len(source_files)} 个PDF文件")
    
    # 获取已处理的文件名
    processed_files = get_pdf_files(processed_folder)
    processed_filenames = set([f[0] for f in processed_files])
    print(f"已处理文件夹中找到 {len(processed_files)} 个PDF文件")
    
    # 找出未处理的文件
    failed_files = [f for f in source_files if f[0] not in processed_filenames]
    print(f"发现 {len(failed_files)} 个未处理的文件")
    
    # 复制失败的文件到目标文件夹
    copied_count = 0
    for filename, full_path, relative_path in failed_files:
        # 生成目标文件路径
        target_file = os.path.join(failed_folder, relative_path)
        
        # 确保目标文件的目录存在
        target_dir = os.path.dirname(target_file)
        os.makedirs(target_dir, exist_ok=True)
        
        # 复制文件
        try:
            print(f"正在复制: {filename}")
            shutil.copy2(full_path, target_file)
            print(f"已复制到: {target_file}")
            copied_count += 1
        except Exception as e:
            print(f"复制失败: {filename} - {str(e)}")
    
    print(f"\n处理完成!")
    print(f"成功复制: {copied_count} 个文件")
    print(f"处理失败: {len(failed_files) - copied_count} 个文件")

if __name__ == "__main__":
    main()