#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

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
    
    print("=" * 60)
    print("文件夹对比分析报告")
    print("=" * 60)
    
    print(f"源文件夹: {source_folder}")
    print(f"已处理文件夹: {processed_folder}")
    print(f"失败文件夹: {failed_folder}")
    
    # 获取所有源文件
    source_files = get_pdf_files(source_folder)
    source_filenames = set([f[0] for f in source_files])
    print(f"\n源文件夹中找到 {len(source_files)} 个PDF文件")
    
    # 获取已处理的文件名
    processed_files = get_pdf_files(processed_folder)
    processed_filenames = set([f[0] for f in processed_files])
    print(f"已处理文件夹中找到 {len(processed_files)} 个PDF文件")
    
    # 获取失败文件夹中的文件名
    failed_files = get_pdf_files(failed_folder)
    failed_filenames = set([f[0] for f in failed_files])
    print(f"失败文件夹中找到 {len(failed_files)} 个PDF文件")
    
    # 1. 检查源文件夹中多出来的文件（应该在失败文件夹中）
    extra_in_source = source_filenames - processed_filenames
    print(f"\n1. 源文件夹中多出来的文件数量: {len(extra_in_source)}")
    
    # 检查这些文件是否都在失败文件夹中
    extra_in_source_in_failed = extra_in_source.intersection(failed_filenames)
    print(f"   其中在失败文件夹中存在的文件数量: {len(extra_in_source_in_failed)}")
    
    if len(extra_in_source) == len(extra_in_source_in_failed):
        print("   ✓ 所有源文件夹中多出的文件都已存放在失败文件夹中")
    else:
        print("   ✗ 有部分源文件夹中多出的文件未存放在失败文件夹中")
        # 列出未在失败文件夹中的文件
        missing_in_failed = extra_in_source - failed_filenames
        print("   未在失败文件夹中的文件:")
        for filename in missing_in_failed:
            print(f"     - {filename}")
    
    # 2. 检查目标文件夹中是否有文件在失败文件夹中（需要删除）
    processed_in_failed = processed_filenames.intersection(failed_filenames)
    print(f"\n2. 目标文件夹中同时存在于失败文件夹中的文件数量: {len(processed_in_failed)}")
    
    if len(processed_in_failed) > 0:
        print("   需要从失败文件夹中删除的文件:")
        for filename in processed_in_failed:
            print(f"     - {filename}")
    else:
        print("   ✓ 失败文件夹中没有与目标文件夹重复的文件")
    
    # 统计总结
    print(f"\n" + "=" * 60)
    print("统计总结")
    print("=" * 60)
    print(f"源文件夹文件总数: {len(source_filenames)}")
    print(f"已处理文件夹文件数: {len(processed_filenames)}")
    print(f"失败文件夹文件数: {len(failed_filenames)}")
    print(f"源文件夹中未处理的文件数: {len(extra_in_source)}")
    print(f"已处理但仍在失败文件夹中的文件数: {len(processed_in_failed)}")

if __name__ == "__main__":
    main()