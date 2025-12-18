#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import shutil

def extract_number_chinese(filename):
    """
    从文件名中提取"数字+三个汉字"的部分
    """
    # 使用正则表达式匹配"数字+三个汉字"的模式
    pattern = r'(\d+[\u4e00-\u9fff]{3})'
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    return None

def find_files_with_pattern(directory):
    """
    遍历目录，找出所有包含"数字+三个汉字"模式的文件
    """
    files_dict = {}
    
    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            pattern_key = extract_number_chinese(file)
            if pattern_key:
                full_path = os.path.join(root, file)
                # 保存文件路径和相对路径
                relative_path = os.path.relpath(root, directory)
                files_dict[pattern_key] = {
                    'full_path': full_path,
                    'filename': file,
                    'relative_path': relative_path
                }
    
    return files_dict

def main():
    # 定义源文件夹和目标文件夹
    source_folder = "/Volumes/TU260Pro/北海案件资料_处理中/缺失文件"
    target_folder = "/Users/yuanliang/Downloads/testpdf/OCRmyPDF处理结果"
    
    # 创建用于存放未找到文件的文件夹
    missing_folder = os.path.join(source_folder, "未在目标文件夹中找到的文件")
    os.makedirs(missing_folder, exist_ok=True)
    
    # 获取源文件夹中的文件
    source_files = find_files_with_pattern(source_folder)
    print(f"源文件夹中找到 {len(source_files)} 个匹配模式的文件")
    
    # 获取目标文件夹中的文件
    target_files = find_files_with_pattern(target_folder)
    print(f"目标文件夹中找到 {len(target_files)} 个匹配模式的文件")
    
    # 查找在目标文件夹中不存在的文件
    missing_files = []
    matched_files = []
    
    for pattern_key, source_info in source_files.items():
        if pattern_key in target_files:
            matched_files.append((pattern_key, source_info, target_files[pattern_key]))
            print(f"匹配成功: {pattern_key}")
        else:
            missing_files.append((pattern_key, source_info))
            print(f"未找到匹配: {pattern_key}")
    
    print(f"\n匹配成功的文件数量: {len(matched_files)}")
    print(f"未在目标文件夹中找到的文件数量: {len(missing_files)}")
    
    # 将未找到的文件复制到单独的文件夹中
    for pattern_key, source_info in missing_files:
        # 保持原有的相对路径结构
        target_subfolder = os.path.join(missing_folder, source_info['relative_path'])
        os.makedirs(target_subfolder, exist_ok=True)
        
        target_file_path = os.path.join(target_subfolder, source_info['filename'])
        
        print(f"正在复制文件: {source_info['filename']}")
        shutil.copy2(source_info['full_path'], target_file_path)
        print(f"已复制到: {target_file_path}")
    
    print("\n处理完成!")

if __name__ == "__main__":
    main()