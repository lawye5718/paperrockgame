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
                files_dict[file] = {
                    'full_path': full_path,
                    'filename': file,
                    'pattern_key': pattern_key,
                    'relative_path': relative_path
                }
    
    return files_dict

def main():
    # 定义源文件夹和目标文件夹（相同路径）
    folder_path = "/Users/yuanliang/Downloads/testpdf/OCRmyPDF处理结果"
    source_subfolder = os.path.join(folder_path, "ocrmypdf")
    target_subfolder = os.path.join(folder_path, "OCRmyPDF_北海案件资料_处理中")
    
    print("=" * 60)
    print("源文件夹和目标文件夹文件对比分析")
    print("=" * 60)
    
    # 获取源文件夹中的文件
    source_files = find_files_with_pattern(source_subfolder)
    print(f"源文件夹中共有 {len(source_files)} 个匹配模式的文件")
    
    # 获取目标文件夹中的文件
    target_files = find_files_with_pattern(target_subfolder)
    print(f"目标文件夹中共有 {len(target_files)} 个匹配模式的文件")
    
    # 收集目标文件夹中的所有模式
    target_patterns = set()
    for filename, info in target_files.items():
        target_patterns.add(info['pattern_key'])
    
    print("\n" + "=" * 60)
    print("详细对比结果")
    print("=" * 60)
    
    # 分析每个源文件是否在目标文件夹中存在匹配
    matching_count = 0
    non_matching_count = 0
    
    for filename, source_info in source_files.items():
        pattern_key = source_info['pattern_key']
        if pattern_key in target_patterns:
            matching_count += 1
            status = "匹配"
        else:
            non_matching_count += 1
            status = "不匹配"
        
        print(f"{status}: {filename} (模式: {pattern_key})")
    
    print("\n" + "=" * 60)
    print("统计结果")
    print("=" * 60)
    print(f"匹配的文件数量: {matching_count}")
    print(f"不匹配的文件数量: {non_matching_count}")
    print(f"总源文件数量: {len(source_files)}")

if __name__ == "__main__":
    main()