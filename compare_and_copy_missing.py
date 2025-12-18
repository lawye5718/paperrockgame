#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil

def get_pdf_files(directory):
    """
    获取目录中的所有PDF文件
    """
    pdf_files = {}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)
                # 使用文件名作为键
                pdf_files[file] = {
                    'full_path': full_path,
                    'relative_path': relative_path
                }
    
    return pdf_files

def main():
    # 定义文件夹路径
    source_folder = "/Volumes/homes/yeweibing/北海案件资料/无密码盘"
    target_folder = "/Volumes/TU260Pro/北海案件资料_处理中/无密码文件"
    failed_folder = "/Volumes/TU260Pro/北海案件资料_处理中/处理失败无密码文件"
    
    print("=" * 60)
    print("文件夹对比和复制工具")
    print("=" * 60)
    
    print(f"源文件夹: {source_folder}")
    print(f"目标文件夹: {target_folder}")
    print(f"失败文件夹: {failed_folder}")
    
    # 获取源文件夹中的所有PDF文件
    source_files = get_pdf_files(source_folder)
    print(f"\n源文件夹中找到 {len(source_files)} 个PDF文件")
    
    # 获取目标文件夹中的所有PDF文件
    target_files = get_pdf_files(target_folder)
    print(f"目标文件夹中找到 {len(target_files)} 个PDF文件")
    
    # 找出源文件夹中有但目标文件夹中没有的文件
    missing_files = {}
    for filename, info in source_files.items():
        if filename not in target_files:
            missing_files[filename] = info
    
    print(f"\n源文件夹中有但目标文件夹中没有的文件数量: {len(missing_files)}")
    
    # 创建失败文件夹（如果不存在）
    os.makedirs(failed_folder, exist_ok=True)
    
    # 将缺失的文件复制到失败文件夹
    copied_count = 0
    for filename, info in missing_files.items():
        source_path = info['full_path']
        relative_path = info['relative_path']
        
        # 生成目标文件路径
        target_path = os.path.join(failed_folder, relative_path)
        
        # 确保目标文件的目录存在
        target_dir = os.path.dirname(target_path)
        os.makedirs(target_dir, exist_ok=True)
        
        # 复制文件
        try:
            print(f"正在复制: {filename}")
            shutil.copy2(source_path, target_path)
            print(f"已复制到: {target_path}")
            copied_count += 1
        except Exception as e:
            print(f"复制失败: {filename} - {str(e)}")
    
    print(f"\n处理完成!")
    print(f"成功复制: {copied_count} 个文件")
    print(f"复制失败: {len(missing_files) - copied_count} 个文件")

if __name__ == "__main__":
    main()