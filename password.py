import os
import pikepdf
p
# --- 配置区域 ---
# 1. 请确认这是挂载后的真实路径，通常在 /Volumes 下
# 建议将文件夹拖入终端获取绝对路径以防出错
input_root = '/Volumes/homes/yeweibing/北海案件资料/原始卷' 
# 或者尝试： input_root = '/Volumes/原始卷' (取决于挂载点名称)

# 2. 输出位置：建议先存在本地桌面，速度快且安全
output_root = os.path.expanduser('~/Desktop/北海案件资料_处理中')ro

pdf_password = '377180'
# ----------------

print(f"开始扫描路径: {input_root}")

processed_count = 0
error_count = 0

# os.walk 实现递归遍历所有子文件夹
for root, dirs, files in os.walk(input_root):
    for filename in files:
        if filename.lower().endswith('.pdf') and not filename.startswith('._'):
            # 构建源文件完整路径
            src_path = os.path.join(root, filename)
            
            # 计算相对路径，用于在输出目录重建结构
            rel_path = os.path.relpath(root, input_root)
            dest_folder = os.path.join(output_root, rel_path)
            
            # 确保目标子文件夹存在
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            
            # --- 关键调整：在此处预先改名 ---
            name_body, ext = os.path.splitext(filename)
            new_filename = f"{name_body}修改版{ext}"
            dest_path = os.path.join(dest_folder, new_filename)
            
            try:
                # 解密并保存
                pdf = pikepdf.open(src_path, password=pdf_password)
                pdf.save(dest_path)
                print(f"[处理成功] {new_filename}")
                processed_count += 1
            except pikepdf.PasswordError:
                print(f"[跳过] 密码错误: {os.path.join(rel_path, filename)}")
                error_count += 1
            except Exception as e:
                print(f"[错误] {filename}: {e}")
                error_count += 1

print(f"\n--- 任务完成 ---")
print(f"共处理文件: {processed_count}")
print(f"错误/跳过: {error_count}")
print(f"文件已保存在桌面的: {output_root}")
print("请继续使用 Acrobat 处理该文件夹。")