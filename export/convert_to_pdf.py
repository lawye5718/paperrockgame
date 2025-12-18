import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def convert_html_to_pdf(html_file, pdf_file):
    """
    将HTML文件转换为PDF文件
    """
    try:
        # 读取HTML文件
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 创建字体配置
        font_config = FontConfiguration()
        
        # 定义CSS样式
        css = CSS(string='''
            @page {
                size: A4 landscape;
                margin: 1cm;
            }
            body {
                font-family: sans-serif;
                margin: 0;
                padding: 0;
            }
        ''', font_config=font_config)
        
        # 转换为PDF
        HTML(string=html_content).write_pdf(pdf_file, stylesheets=[css], font_config=font_config)
        print(f"成功将 {html_file} 转换为 {pdf_file}")
        return True
    except Exception as e:
        print(f"转换过程中出错: {str(e)}")
        return False

def main():
    # 定义文件路径
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    pdf_path = os.path.join(os.path.dirname(__file__), '..', '北海案件关系图.pdf')
    
    # 检查HTML文件是否存在
    if not os.path.exists(html_path):
        print(f"错误: 找不到HTML文件 {html_path}")
        return
    
    # 执行转换
    success = convert_html_to_pdf(html_path, pdf_path)
    
    if success:
        print(f"PDF文件已保存到: {pdf_path}")
    else:
        print("PDF转换失败")

if __name__ == "__main__":
    main()