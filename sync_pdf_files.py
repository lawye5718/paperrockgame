#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import re
from pathlib import Path

def extract_file_identifier(filename):
    """从文件名中提取数字+移送卷作为唯一标识符"""
    # 更简单的匹配方式，直接匹配数字+移送卷
    pattern = r'(\d+移送卷)'
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    
    # 备用方案：匹配数字+任意两个汉字
    pattern2 = r'(\d+[一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟]{2})'
    match2 = re.search(pattern2, filename)
    return match2.group(1) if match2 else None

def get_pdf_files_with_identifier(directory):
    """获取目录及其子目录中的所有PDF文件，并提取标识符"""
    pdf_files = {}
    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        return pdf_files
        
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                identifier = extract_file_identifier(file)
                if identifier:
                    # 使用标识符作为键
                    relative_path = os.path.relpath(os.path.join(root, file), directory)
                    pdf_files[identifier] = {
                        'full_path': os.path.join(root, file),
                        'relative_path': relative_path
                    }
                else:
                    print(f"警告: 无法从文件名提取标识符: {file}")
    return pdf_files

def get_pdf_files(directory):
    """获取目录及其子目录中的所有PDF文件"""
    pdf_files = {}
    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        return pdf_files
        
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                # 使用相对路径作为键，便于比较
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                pdf_files[relative_path] = os.path.join(root, file)
    return pdf_files

def sync_missing_files(source_dir, target_dir, missing_dir_name="缺失文件"):
    """同步缺失的文件（基于文件标识符匹配）"""
    print(f"\n正在比较:\n  源目录: {source_dir}\n  目标目录: {target_dir}")
    
    source_pdfs = get_pdf_files_with_identifier(source_dir)
    target_pdfs = get_pdf_files_with_identifier(target_dir)
    
    missing_dir = os.path.join(target_dir, missing_dir_name)
    os.makedirs(missing_dir, exist_ok=True)
    
    missing_count = 0
    for identifier, source_info in source_pdfs.items():
        if identifier not in target_pdfs:
            print(f"发现缺失文件 (标识符: {identifier}): {source_info['relative_path']}")
            # 保持目录结构
            target_path = os.path.join(missing_dir, source_info['relative_path'])
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            try:
                shutil.copy2(source_info['full_path'], target_path)
                print(f"  已复制到: {target_path}")
                missing_count += 1
            except Exception as e:
                print(f"  复制失败: {e}")
                
    print(f"总共从 {source_dir} 同步了 {missing_count} 个缺失文件到 {missing_dir}")
    return missing_count

def sync_ocr_files(source_dir, target_dir, ocr_dir_name="ocrmypdf"):
    """同步OCR处理结果文件（基于文件标识符匹配）"""
    print(f"\n正在比较:\n  源目录: {source_dir}\n  目标目录: {target_dir}")
    
    source_pdfs = get_pdf_files_with_identifier(source_dir)
    target_pdfs = get_pdf_files_with_identifier(target_dir)
    
    ocr_dir = os.path.join(target_dir, ocr_dir_name)
    os.makedirs(ocr_dir, exist_ok=True)
    
    synced_count = 0
    for identifier, source_info in source_pdfs.items():
        if identifier not in target_pdfs:
            print(f"发现缺失的OCR文件 (标识符: {identifier}): {source_info['relative_path']}")
            # 保持目录结构
            target_path = os.path.join(ocr_dir, source_info['relative_path'])
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            try:
                shutil.copy2(source_info['full_path'], target_path)
                print(f"  已复制到: {target_path}")
                synced_count += 1
            except Exception as e:
                print(f"  复制失败: {e}")
                
    print(f"总共从 {source_dir} 同步了 {synced_count} 个OCR文件到 {ocr_dir}")
    return synced_count

def compare_directories(dir1, dir2):
    """比较两个目录中的PDF文件（基于文件标识符匹配）"""
    print(f"\n正在比较目录:\n  目录1: {dir1}\n  目录2: {dir2}")
    
    dir1_pdfs = get_pdf_files_with_identifier(dir1)
    dir2_pdfs = get_pdf_files_with_identifier(dir2)
    
    only_in_dir1 = set(dir1_pdfs.keys()) - set(dir2_pdfs.keys())
    only_in_dir2 = set(dir2_pdfs.keys()) - set(dir1_pdfs.keys())
    
    print(f"仅在 {dir1} 中的文件数量: {len(only_in_dir1)}")
    print(f"仅在 {dir2} 中的文件数量: {len(only_in_dir2)}")
    
    if only_in_dir1:
        print(f"\n仅在 {dir1} 中的文件:")
        for identifier in sorted(only_in_dir1):
            file_info = dir1_pdfs[identifier]
            print(f"  [{identifier}] {file_info['relative_path']}")
            
    if only_in_dir2:
        print(f"\n仅在 {dir2} 中的文件:")
        for identifier in sorted(only_in_dir2):
            file_info = dir2_pdfs[identifier]
            print(f"  [{identifier}] {file_info['relative_path']}")
    
    return only_in_dir1, only_in_dir2

def main():
    # 定义各个目录路径
    original_volume = "/Volumes/TU260Pro/北海案件资料_处理中/原始卷"
    ocr_volume = "/Volumes/TU260Pro/北海案件资料_处理中/北海ocr"
    ocrmypdf_results = "/Users/yuanliang/Downloads/testpdf/OCRmyPDF处理结果/ocrmypdf"
    network_original = "/Volumes/homes/yeweibing/北海案件资料/原始卷"
    
    print("=" * 60)
    print("PDF文件同步工具")
    print("=" * 60)
    
    # 检查必要的目录是否存在
    if not os.path.exists(original_volume):
        print(f"警告: 原始卷目录不存在: {original_volume}")
        return
        
    if not os.path.exists(ocr_volume):
        print(f"警告: 北海OCR目录不存在: {ocr_volume}")
        return
    
    # (1) 比较原始卷和北海ocr，同步缺失的PDF文件
    print("\n[任务1] 同步原始卷中缺失的PDF文件到北海ocr...")
    sync_missing_files(original_volume, ocr_volume, "缺失文件")
    
    # (2) 检查OCRmyPDF处理结果，同步到北海ocr下的ocrmypdf文件夹
    if os.path.exists(ocrmypdf_results):
        print("\n[任务2] 同步OCRmyPDF处理结果到北海ocr...")
        sync_ocr_files(ocrmypdf_results, ocr_volume, "ocrmypdf")
    else:
        print(f"\n警告: OCRmyPDF处理结果目录不存在: {ocrmypdf_results}")
        
    # (3) 比较目录内容
    print("\n[任务3] 比较目录内容...")
    compare_directories(original_volume, ocr_volume)
    compare_directories(ocrmypdf_results, ocr_volume)
        
    # (4) 检查网络路径中的文件，如果在北海ocr中找不到，则复制到缺失文件夹中
    if os.path.exists(network_original):
        print("\n[任务4] 同步网络驱动器中的缺失文件到北海ocr...")
        sync_missing_files(network_original, ocr_volume, "缺失文件")
    else:
        print(f"\n警告: 网络原始卷目录不存在: {network_original}")
    
    print("\n" + "=" * 60)
    print("同步任务完成")
    print("=" * 60)

if __name__ == "__main__":
    main()