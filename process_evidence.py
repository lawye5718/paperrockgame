#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import pandas as pd

# 配置输入和输出目录
INPUT_DIR = "/Users/yuanliang/Downloads/testpdf/ocr1127/已处理/"  # 默认输入目录
OUTPUT_DIR = "/Users/yuanliang/Downloads/testpdf/ocr1127/已处理/processed_tables"  # 输出MD表格的文件夹
EXCEL_FILENAME = "/Users/yuanliang/Downloads/testpdf/ocr1127/已处理/证据提取总表.xlsx"

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def is_date(text):
    """判断是否为日期格式 (支持 20250101, 20210101-20220101, 2021.01.01)"""
    # 移除常见日期分隔符
    clean_text = text.replace('.', '').replace('-', '').replace('—', '').replace('/', '').replace(' ', '')
    # 匹配8位数字或两个8位数字的范围 (简单版)
    if re.match(r'^(20\d{6}|19\d{6}|20\d{6}\d{8})$', clean_text):
        return True
    return False

def extract_cover_title(cover_text):
    """提取封面中的有效标题"""
    lines = [line.strip() for line in cover_text.split('\n') if line.strip()]
    
    # 策略1：优先找“卷X：...”
    for line in lines:
        if re.match(r'^卷[一二三四五六七八九十0-9]+[：:].*', line):
            return line
            
    # 策略2：包含关键证据类型的长标题
    for line in lines:
        if ("书证" in line or "笔录" in line) and len(line) > 5:
            return line
            
    # 策略3：兜底，找包含“案”的行
    for line in lines:
        if "案" in line and len(line) > 4 and "案件名称" not in line and "案卷" not in line:
            return line
            
    return "未找到特定标题"

def clean_ocr_line(line):
    """清洗OCR单行文本，去除列表符号"""
    line = line.strip()
    # 去除开头的 '- ', '* ', '1. ' 等列表标记
    # 注意：不要误删纯数字，因为那可能是序号
    if re.match(r'^[-*]\s+', line):
        line = re.sub(r'^[-*]\s+', '', line)
    return line

def parse_directory_content(dir_text):
    """
    解析目录文本，采用【序号流锚点切分法】。
    """
    if not dir_text:
        return []

    lines = [clean_ocr_line(l) for l in dir_text.split('\n') if l.strip()]
    
    # === 关键修复：精确的表头过滤 ===
    # 只有当行内容完全等于以下词汇时才过滤，防止误删包含"名"的正文
    exact_headers = {'卷内文件目录', '顺序号', '文号', '责任者', '题名', '题', '名', '日期', '页号', '备注', '目录页'}
    
    cleaned_lines_with_idx = []
    for line in lines:
        # 1. 过滤完全匹配的表头
        if line in exact_headers:
            continue
        # 2. 过滤 Markdown 标题
        if line.startswith('###'):
            continue
        # 3. 过滤纯符号
        if re.match(r'^[\[\]\(\)\【\】\-]+$', line):
            continue
            
        cleaned_lines_with_idx.append(line)
        
    if not cleaned_lines_with_idx:
        return []

    # === 步骤2：构建数据流 ===
    data_stream = []
    for line in cleaned_lines_with_idx:
        dtype = 'text'
        # 严格的序号匹配：纯数字，1到3位
        if re.match(r'^\d{1,3}$', line):
            dtype = 'number'
        elif is_date(line):
            dtype = 'date'
        
        data_stream.append({'text': line, 'type': dtype})

    # === 步骤3：寻找最长序号流 (Sequence Stream) ===
    # 我们寻找 1, 2, 3, 4... 这样的递增序列
    seq_map = {} # seq_num -> list of indices in data_stream
    for idx, item in enumerate(data_stream):
        if item['type'] == 'number':
            val = int(item['text'])
            if val not in seq_map:
                seq_map[val] = []
            seq_map[val].append(idx)
    
    # 寻找最佳的 1, 2, 3... 路径
    matched_indices = []
    
    # 尝试找到起始点 1
    start_candidates = seq_map.get(1, [])
    
    if not start_candidates:
        # 如果没有序号1，可能是OCR没识别出来。
        # 这里可以做一个复杂的兜底（比如按日期分割），但为保稳健，暂时返回空
        # 或者如果有日期，按日期强行分割
        has_dates = any(d['type'] == 'date' for d in data_stream)
        if has_dates:
            # TODO: Add date-based fallback if needed
            pass
    else:
        # 贪心算法：从第一个1开始，找后面最近的2，再找最近的3...
        # 如果有多个1，我们取能构成最长链的那个（简化起见，取第一个能连上2的）
        
        best_path = []
        for start_idx in start_candidates:
            current_path = [{'seq': 1, 'idx': start_idx}]
            last_idx = start_idx
            expect = 2
            
            while True:
                next_candidates = seq_map.get(expect, [])
                valid_next = [n for n in next_candidates if n > last_idx]
                
                if not valid_next:
                    break
                
                # 取第一个有效的
                next_idx = valid_next[0]
                current_path.append({'seq': expect, 'idx': next_idx})
                last_idx = next_idx
                expect += 1
            
            if len(current_path) > len(best_path):
                best_path = current_path
        
        matched_indices = best_path

    # 如果还是没找到序列（比如只有一个1，或者没找到1），尝试放宽条件
    # 如果只有一个1，也接受
    if not matched_indices and start_candidates:
        matched_indices = [{'seq': 1, 'idx': start_candidates[0]}]

    items = []
    
    if not matched_indices:
        return [] # 实在无法解析
        
    # === 步骤4：确定锚点模式 (Start vs End) ===
    # 检查序号1和它之前的日期
    first_seq_idx = matched_indices[0]['idx']
    
    # 在序号1之前找最近的一个日期
    date_before_idx = -1
    for i in range(first_seq_idx - 1, -1, -1):
        if data_stream[i]['type'] == 'date':
            date_before_idx = i
            break
            
    # 如果序号1之前紧挨着日期（距离很近，比如5行以内），那多半是 End-anchored (文本..日期..序号)
    # 如果序号1之前很远才有日期，或者根本没有日期，那是 Start-anchored
    
    is_start_anchored = True
    if date_before_idx != -1:
        # 检查距离
        if first_seq_idx - date_before_idx < 5:
            is_start_anchored = False
            
    # === 步骤5：切分并提取 ===
    for i, anchor in enumerate(matched_indices):
        seq_num = anchor['seq']
        idx = anchor['idx']
        
        block = []
        
        if is_start_anchored:
            # 范围：[当前序号+1, 下一个序号)
            start = idx + 1
            if i < len(matched_indices) - 1:
                end = matched_indices[i+1]['idx']
            else:
                end = len(data_stream)
            block = data_stream[start:end]
            
        else: # End-anchored
            # 范围：(上一个序号+1, 当前序号) 
            # 注意：End-anchored模式下，序号是结尾。内容在序号之前。
            # 第一项的起点通常是0或者上一个条目结束的地方
            if i == 0:
                start = 0
            else:
                start = matched_indices[i-1]['idx'] + 1
            end = idx # 不包含当前序号
            block = data_stream[start:end]
            
        # 块内提取
        item_text_parts = []
        item_date = ''
        item_page = ''
        
        for bit in block:
            if bit['type'] == 'date':
                # 如果有多个日期，取第一个（通常是开始日期）
                if not item_date: 
                    item_date = bit['text']
            elif bit['type'] == 'number':
                # 块内的其他数字视为页码
                item_page = bit['text']
            else:
                item_text_parts.append(bit['text'])
                
        # 简单的合并
        full_title = "".join(item_text_parts)
        
        # 只有当提取到了有效内容才添加，防止空行
        if full_title or item_date or item_page:
            items.append({
                'seq': seq_num,
                'title': full_title,
                'remark': '', # 暂时置空，人工校对
                'page': item_page,
                'date': item_date
            })
            
    return items

def process_all_files():
    ensure_dir(OUTPUT_DIR)
    
    all_excel_rows = []
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.md') and "Table_" not in f] # 排除生成的表格
    files.sort()
    
    print(f"开始处理 {len(files)} 个文件...")

    for idx, filename in enumerate(files):
        file_path = os.path.join(INPUT_DIR, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Skipping {filename}: {e}")
            continue

        # 分割封面和目录
        # 增强正则，适应可能的换行
        parts = re.split(r'^##\s+目录内容', content, flags=re.MULTILINE)
        
        cover_text = parts[0]
        dir_text = parts[1] if len(parts) > 1 else ""
        
        # 如果 split 失败，尝试旧方法
        if not dir_text and "## 目录内容" in content:
             dir_text = content.split("## 目录内容")[1]

        file_title = extract_cover_title(cover_text)
        evidence_items = parse_directory_content(dir_text)
        
        # 准备 Markdown
        md_lines = []
        md_lines.append(f"# {filename} 表格化数据")
        md_lines.append(f"**文件标题**: {file_title}\n")
        md_lines.append("| 顺序号 | 证据名称 | 证明目的 | 页号 | 日期 |")
        md_lines.append("|---|---|---|---|---|")
        
        if not evidence_items:
            md_lines.append("| - | 未找到目录项 | - | - | - |")
            all_excel_rows.append({
                'MD文件序号': idx + 1,
                'MD文件名': filename,
                '文件标题': file_title,
                '证据名称': '未找到目录项',
                '证明目的': '',
                '页码': ''
            })
        else:
            for item in evidence_items:
                clean_title = item['title'].replace('\n', ' ').replace('|', ' ')
                line = f"| {item['seq']} | {clean_title} | {item['remark']} | {item['page']} | {item['date']} |"
                md_lines.append(line)
                
                all_excel_rows.append({
                    'MD文件序号': idx + 1,
                    'MD文件名': filename,
                    '文件标题': file_title,
                    '证据名称': clean_title,
                    '证明目的': item['remark'],
                    '页码': item['page']
                })
        
        new_md_name = f"Table_{filename}"
        out_path = os.path.join(OUTPUT_DIR, new_md_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(md_lines))

    # 生成 Excel
    if all_excel_rows:
        df = pd.DataFrame(all_excel_rows)
        cols = ['MD文件序号', 'MD文件名', '文件标题', '证据名称', '证明目的', '页码']
        for c in cols:
            if c not in df.columns: df[c] = ''
        df = df[cols]
        
        df.to_excel(EXCEL_FILENAME, index=False)
        print(f"\n成功! Excel已生成: {EXCEL_FILENAME}")
        print(f"MD表格已生成在: {OUTPUT_DIR}")
    else:
        print("\n警告: 未提取到数据。")

if __name__ == "__main__":
    process_all_files()