# -*- coding: utf-8 -*-
"""
芯片产品作战看板 - 静态 HTML 报告生成器
KR 的芯片自动化工作流指挥中心（独立运行版本）

功能:
1. 从数据库加载产品数据
2. 生成静态 HTML 报告
3. 无需启动 Streamlit 服务器

使用方法:
    python chip_report_generator.py

输出:
    在 reports/ 目录生成 chip_dashboard_YYYYMMDD_HHMMSS.html 文件

作者：KR + Claude Code
日期：2026-03-23
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 导入本地数据库模块
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from database import (
    init_database,
    ProductManager,
    ensure_database_initialized
)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'chip_products.db')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_products_from_db():
    """从数据库加载产品数据"""
    try:
        ensure_database_initialized()
        db_products = ProductManager.get_all_products()

        products = []
        status_map = {
            'active': '已上架',
            'pending': '待上架',
            'reviewing': '审核中',
            'offline': '已下架'
        }

        for prod in db_products:
            db_status = prod.get('status', 'pending')
            products.append({
                'id': prod.get('id'),
                '型号': prod.get('model', ''),
                '名称': prod.get('name', ''),
                '品牌': prod.get('brand', '冠辰科技'),
                '分类': prod.get('category', 'LED 驱动芯片'),
                '电压': prod.get('input_voltage', 'N/A'),
                '功率': prod.get('power', 'N/A'),
                '封装': prod.get('package', 'N/A'),
                '温度': prod.get('temp_range', 'N/A'),
                '成本': prod.get('cost', '待核算'),
                '建议售价': prod.get('price', '待定价'),
                '状态': status_map.get(db_status, db_status),
                '上架平台': prod.get('platform', 'N/A'),
                '创建时间': prod.get('created_at', 'N/A')
            })

        return products
    except Exception as e:
        print(f"加载产品数据失败：{e}")
        return []


def generate_kpi_cards(products):
    """生成 KPI 卡片 HTML"""
    total = len(products)
    active = sum(1 for p in products if p.get('状态') == '已上架')
    pending = sum(1 for p in products if p.get('状态') == '待上架')
    reviewing = sum(1 for p in products if p.get('状态') == '审核中')

    kpi_data = [
        {'title': '产品总数', 'value': total, 'color': '#667eea', 'icon': '📦'},
        {'title': '已上架', 'value': active, 'color': '#10b981', 'icon': '✅'},
        {'title': '待上架', 'value': pending, 'color': '#f59e0b', 'icon': '⏳'},
        {'title': '审核中', 'value': reviewing, 'color': '#3b82f6', 'icon': '🔍'},
    ]

    cards_html = ''
    for kpi in kpi_data:
        cards_html += f'''
        <div class="kpi-card" style="background: linear-gradient(135deg, {kpi['color']}, {kpi['color']}dd);">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{kpi['icon']}</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">{kpi['title']}</div>
            <div style="font-size: 2.5rem; font-weight: bold; margin-top: 0.5rem;">{kpi['value']}</div>
        </div>
        '''

    return cards_html


def generate_product_table(products):
    """生成产品表格 HTML"""
    if not products:
        return '''
        <div class="empty-state">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📭</div>
            <h3>暂无产品数据</h3>
            <p>请先添加产品或上传 PDF 规格书</p>
        </div>
        '''

    rows = ''
    for i, p in enumerate(products):
        status_class = {
            '已上架': 'status-success',
            '待上架': 'status-warning',
            '审核中': 'status-info',
            '已下架': 'status-danger'
        }.get(p.get('状态'), 'status-info')

        rows += f'''
        <tr>
            <td style="font-weight: 600; color: #1f2937;">{p.get('型号', 'N/A')}</td>
            <td>{p.get('名称', 'N/A')}</td>
            <td>{p.get('品牌', '冠辰科技')}</td>
            <td>{p.get('分类', 'LED 驱动芯片')}</td>
            <td>{p.get('电压', 'N/A')}</td>
            <td>{p.get('功率', 'N/A')}</td>
            <td>{p.get('封装', 'N/A')}</td>
            <td>{p.get('成本', '待核算')}</td>
            <td>{p.get('建议售价', '待定价')}</td>
            <td><span class="status-badge {status_class}">{p.get('状态', 'N/A')}</span></td>
        </tr>
        '''

    return f'''
    <div class="table-container">
        <table class="product-table">
            <thead>
                <tr>
                    <th>型号</th>
                    <th>产品名称</th>
                    <th>品牌</th>
                    <th>分类</th>
                    <th>电压</th>
                    <th>功率</th>
                    <th>封装</th>
                    <th>成本</th>
                    <th>建议售价</th>
                    <th>状态</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    '''


def generate_html_report(products, output_path=None):
    """生成完整的 HTML 报告"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report_date = datetime.now().strftime('%Y年%m月%d日')

    kpi_cards = generate_kpi_cards(products)
    product_table = generate_product_table(products)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>冠辰科技作战指挥中心 - {now}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Microsoft YaHei', 'PingFang SC', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            font-size: 2.5rem;
            color: #1f2937;
            margin-bottom: 10px;
        }}

        .header p {{
            color: #6b7280;
            font-size: 1.1rem;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .kpi-card {{
            background: white;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            color: white;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            transition: transform 0.3s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-5px);
        }}

        .content-section {{
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}

        .section-title {{
            font-size: 1.5rem;
            color: #1f2937;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }}

        .table-container {{
            overflow-x: auto;
        }}

        .product-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .product-table th,
        .product-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}

        .product-table th {{
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
            position: sticky;
            top: 0;
        }}

        .product-table tr:hover {{
            background: #f9fafb;
        }}

        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }}

        .status-success {{ background-color: #10b981; color: white; }}
        .status-warning {{ background-color: #f59e0b; color: white; }}
        .status-info {{ background-color: #3b82f6; color: white; }}
        .status-danger {{ background-color: #ef4444; color: white; }}

        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #9ca3af;
        }}

        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 20px;
        }}

        .print-btn {{
            background: white;
            color: #667eea;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 20px;
        }}

        .print-btn:hover {{
            background: #f9fafb;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .print-btn {{
                display: none;
            }}
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.75rem;
            }}
            .kpi-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 冠辰科技作战指挥中心</h1>
            <p>CHIP TECHNOLOGY COMMAND CENTER | 生成时间：{now}</p>
        </div>

        <button class="print-btn" onclick="window.print()">🖨️ 打印报告</button>

        <div class="kpi-grid">
            {kpi_cards}
        </div>

        <div class="content-section">
            <h2 class="section-title">📊 产品数据列表</h2>
            {product_table}
        </div>

        <div class="footer">
            <p>© 2026 冠辰科技有限公司 | 报告生成日期：{report_date}</p>
            <p style="margin-top: 10px; font-size: 0.9rem;">
                本报告由芯片自动化工作流系统自动生成
            </p>
        </div>
    </div>

    <script>
        // 添加简单的交互效果
        document.querySelectorAll('.kpi-card').forEach(card => {{
            card.addEventListener('click', function() {{
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {{
                    this.style.transform = '';
                }}, 150);
            }});
        }});

        console.log('报告加载完成：{now}');
    </script>
</body>
</html>
'''

    # 生成文件名
    if output_path is None:
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(reports_dir, f'chip_dashboard_{timestamp}.html')

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path


def main():
    """主函数"""
    print("=" * 60)
    print("🎯 冠辰科技作战指挥中心 - 静态 HTML 报告生成器")
    print("=" * 60)
    print()

    # 加载产品数据
    print("📂 正在从数据库加载产品数据...")
    products = load_products_from_db()

    if not products:
        print("⚠️  数据库中没有产品数据")
        print("💡 请先添加产品或运行产品导入脚本")
    else:
        print(f"✅ 已加载 {len(products)} 个产品")

    # 统计状态
    status_count = {}
    for p in products:
        status = p.get('状态', '未知')
        status_count[status] = status_count.get(status, 0) + 1

    print()
    print("📊 产品状态统计:")
    for status, count in status_count.items():
        print(f"   {status}: {count} 个")

    # 生成 HTML 报告
    print()
    print("📝 正在生成 HTML 报告...")
    output_path = generate_html_report(products)
    print(f"✅ 报告已生成：{output_path}")
    print()

    # 转换成本地文件路径
    file_url = f"file:///{output_path.replace(os.sep, '/')}"
    print(f"🌐 用浏览器打开：{file_url}")
    print()
    print("=" * 60)
    print("✨ 报告生成完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
