#!/usr/bin/env python
"""
PDF 报价单解析器 - 宜欧特自动化工作流
功能：自动解析 PDF 报价单，提取产品信息，生成 Excel 表格
"""

import pdfplumber
import pandas as pd
import json
import sys
from pathlib import Path
from datetime import datetime

def parse_pdf_quote(pdf_path):
    """解析 PDF 报价单"""
    print(f"📄 正在处理：{pdf_path}")

    data = []

    with pdfplumber.open(pdf_path) as pdf:
        print(f"  共 {len(pdf.pages)} 页")

        for i, page in enumerate(pdf.pages, 1):
            print(f"  处理第 {i} 页...")

            # 提取表格
            tables = page.extract_tables()

            for table in tables:
                for row in table:
                    if row and len(row) >= 3:
                        # 智能识别产品行
                        product_info = {
                            '页码': i,
                            '产品型号': str(row[0]).strip() if row[0] else '',
                            '产品名称': str(row[1]).strip() if row[1] else '',
                            '规格参数': str(row[2]).strip() if row[2] else '',
                            '单价': str(row[3]).strip() if len(row) > 3 and row[3] else '',
                            '数量': str(row[4]).strip() if len(row) > 4 and row[4] else '',
                            '金额': str(row[5]).strip() if len(row) > 5 and row[5] else '',
                            '备注': str(row[6]).strip() if len(row) > 6 and row[6] else '',
                        }
                        data.append(product_info)

    return data

def save_to_excel(data, output_path):
    """保存为 Excel 文件"""
    if not data:
        print("⚠️ 未提取到数据")
        return False

    df = pd.DataFrame(data)

    # 保存到 Excel
    df.to_excel(output_path, index=False, engine='openpyxl')
    print(f"✅ 已保存到：{output_path}")
    print(f"   共 {len(data)} 条记录")

    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python parse_pdf_quote.py <PDF 文件路径> [输出 Excel 路径]")
        print("\n示例:")
        print("  python parse_pdf_quote.py quote.pdf")
        print("  python parse_pdf_quote.py quote.pdf output.xlsx")
        return

    pdf_path = sys.argv[1]

    # 检查文件是否存在
    if not Path(pdf_path).exists():
        print(f"❌ 文件不存在：{pdf_path}")
        return

    # 生成输出路径
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        base_name = Path(pdf_path).stem
        output_dir = Path(pdf_path).parent
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = output_dir / f"{base_name}_解析结果_{timestamp}.xlsx"

    # 解析 PDF
    data = parse_pdf_quote(pdf_path)

    # 保存 Excel
    if data:
        save_to_excel(data, output_path)
        print("\n🎉 解析完成！")
    else:
        print("\n⚠️ 未能提取到表格数据，请检查 PDF 格式")

if __name__ == "__main__":
    main()
