#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil

# 需要查找并复制的文件列表
files_to_copy = [
    "102移送卷（王雄昌）修改版_processed.pdf",
    "103移送卷（王雄昌）修改版_processed.pdf",
    "104移送卷（王雄昌）修改版_processed.pdf",
    "105移送卷（王雄昌）修改版_processed.pdf",
    "106移送卷（王雄昌）修改版_processed.pdf",
    "107移送卷（王雄昌）修改版_processed.pdf",
    "108移送卷（王雄昌）修改版_processed.pdf",
    "109移送卷（王雄昌）修改版_processed.pdf",
    "110移送卷（王雄昌）修改版_processed.pdf",
    "166移送卷（王雄昌）修改版_processed.pdf",
    "167移送卷（王雄昌）修改版_processed.pdf",
    "168移送卷（王雄昌）修改版_processed.pdf",
    "169移送卷（王雄昌）修改版_processed.pdf",
    "170移送卷（王雄昌）修改版_processed.pdf",
    "171移送卷（王雄昌）修改版_processed.pdf",
    "172移送卷（王雄昌）修改版_processed.pdf",
    "173移送卷（王雄昌）修改版_processed.pdf",
    "174移送卷（王雄昌）修改版_processed.pdf",
    "175移送卷（王雄昌）修改版_processed.pdf",
    "176移送卷（王雄昌）修改版_processed.pdf",
    "177移送卷（王雄昌）修改版_processed.pdf",
    "178移送卷（王雄昌）修改版_processed.pdf",
    "179移送卷（王雄昌）修改版_processed.pdf",
    "41移送卷（王雄昌）修改版_processed.pdf",
    "42移送卷（王雄昌）修改版_processed.pdf",
    "43移送卷（王雄昌）修改版_processed.pdf",
    "45移送卷（王雄昌）修改版_processed.pdf",
    "46移送卷（王雄昌）修改版_processed.pdf",
    "48移送卷（王雄昌）修改版_processed.pdf",
    "51移送卷（王雄昌）修改版_processed.pdf",
    "52移送卷（王雄昌）修改版_processed.pdf",
    "56移送卷（王雄昌）修改版_processed.pdf",
    "58移送卷（王雄昌）修改版_processed.pdf",
    "59移送卷（王雄昌）修改版_processed.pdf",
    "60移送卷（王雄昌）修改版_processed.pdf"
]

def find_and_copy_files(source_dir, target_dir):
    """
    在源目录中查找指定文件并复制到目标目录
    """
    copied_files = []
    missing_files = []
    
    print("开始扫描目录查找文件...")
    
    # 遍历源目录及其子目录查找文件
    for root, dirs, files in os.walk(source_dir):
        # 跳过目标目录本身，避免复制到自身
        if os.path.abspath(root).startswith(os.path.abspath(target_dir)):
            continue
            
        for file in files:
            if file in files_to_copy:
                source_path = os.path.join(root, file)
                # 保持相对路径结构
                relative_path = os.path.relpath(root, source_dir)
                target_path_dir = os.path.join(target_dir, relative_path)
                target_path = os.path.join(target_path_dir, file)
                
                # 创建目标目录
                os.makedirs(target_path_dir, exist_ok=True)
                
                # 复制文件
                print(f"复制文件: {source_path}")
                print(f"        -> {target_path}")
                shutil.copy2(source_path, target_path)
                copied_files.append(file)
                print(f"完成复制: {file}")
    
    # 检查是否有文件未找到
    for file in files_to_copy:
        if file not in copied_files:
            missing_files.append(file)
    
    return copied_files, missing_files

def main():
    # 定义路径
    source_directory = "/Volumes/homes/yeweibing/北海案件资料/处理案卷材料"
    target_directory = "/Volumes/homes/yeweibing/北海案件资料/处理案卷材料/需重新上传"
    
    # 检查目录是否存在
    if not os.path.exists(source_directory):
        print(f"源目录不存在: {source_directory}")
        return
    
    print("开始查找并复制文件...")
    print(f"源目录: {source_directory}")
    print(f"目标目录: {target_directory}")
    
    # 执行文件查找和复制
    copied_files, missing_files = find_and_copy_files(source_directory, target_directory)
    
    print(f"\n成功复制 {len(copied_files)} 个文件:")
    for file in copied_files:
        print(f"  - {file}")
    
    if missing_files:
        print(f"\n未找到 {len(missing_files)} 个文件:")
        for file in missing_files:
            print(f"  - {file}")
    else:
        print("\n所有文件都已找到并复制完成!")
    
    print("\n文件复制完成!")

if __name__ == "__main__":
    main()