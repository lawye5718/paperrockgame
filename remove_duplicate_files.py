#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

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
    # 定义源文件夹和目标文件夹（相同路径）
    folder_path = "/Users/yuanliang/Downloads/testpdf/OCRmyPDF处理结果"
    source_subfolder = os.path.join(folder_path, "ocrmypdf")
    target_subfolder = os.path.join(folder_path, "OCRmyPDF_北海案件资料_处理中")
    
    print(f"源文件夹: {source_subfolder}")
    print(f"目标文件夹: {target_subfolder}")
    
    # 获取源文件夹中的文件
    source_files = find_files_with_pattern(source_subfolder)
    print(f"\n源文件夹中找到 {len(source_files)} 个匹配模式的文件")
    
    # 获取目标文件夹中的文件
    target_files = find_files_with_pattern(target_subfolder)
    print(f"目标文件夹中找到 {len(target_files)} 个匹配模式的文件")
    
    # 查找在目标文件夹中存在的文件（需要删除）
    files_to_delete = []
    files_to_keep = []
    
    for pattern_key, source_info in source_files.items():
        if pattern_key in target_files:
            files_to_delete.append((pattern_key, source_info))
            print(f"需要删除: {pattern_key}")
        else:
            files_to_keep.append((pattern_key, source_info))
            print(f"需要保留: {pattern_key}")
    
    print(f"\n需要删除的文件数量: {len(files_to_delete)}")
    print(f"需要保留的文件数量: {len(files_to_keep)}")
    
    # 删除在目标文件夹中已存在的文件
    for pattern_key, source_info in files_to_delete:
        file_path = source_info['full_path']
        print(f"正在删除文件: {file_path}")
        try:
            os.remove(file_path)
            print(f"已删除: {file_path}")
        except Exception as e:
            print(f"删除失败 {file_path}: {e}")
    
    print("\n处理完成!")

if __name__ == "__main__":
    main()
