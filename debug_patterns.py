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
    
    print("=" * 50)
    print("详细分析文件名模式")
    print("=" * 50)
    
    # 获取源文件夹中的文件
    source_files = find_files_with_pattern(source_subfolder)
    print(f"源文件夹 ({source_subfolder}) 中的文件:")
    for filename, info in source_files.items():
        print(f"  文件名: {filename}")
        print(f"    提取模式: {info['pattern_key']}")
        print(f"    完整路径: {info['full_path']}")
    
    print("\n" + "=" * 50)
    
    # 获取目标文件夹中的文件
    target_files = find_files_with_pattern(target_subfolder)
    print(f"目标文件夹 ({target_subfolder}) 中的部分文件 (前10个):")
    count = 0
    target_patterns = set()
    for filename, info in target_files.items():
        if count >= 10:
            print(f"  ... 还有 {len(target_files) - 10} 个文件")
            break
        print(f"  文件名: {filename}")
        print(f"    提取模式: {info['pattern_key']}")
        target_patterns.add(info['pattern_key'])
        print(f"    完整路径: {info['full_path']}")
        count += 1
    
    print("\n" + "=" * 50)
    print("模式匹配分析")
    print("=" * 50)
    
    # 分析匹配情况
    matching_patterns = []
    non_matching_patterns = []
    
    source_patterns = set()
    for filename, info in source_files.items():
        source_patterns.add(info['pattern_key'])
        if info['pattern_key'] in target_patterns:
            matching_patterns.append(info['pattern_key'])
        else:
            non_matching_patterns.append(info['pattern_key'])
    
    print(f"源文件夹中的唯一模式: {sorted(source_patterns)}")
    print(f"目标文件夹中的唯一模式 (部分): {sorted(list(target_patterns)[:10])}")
    print(f"匹配的模式: {matching_patterns}")
    print(f"不匹配的模式: {non_matching_patterns}")

if __name__ == "__main__":
    main()