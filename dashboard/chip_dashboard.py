# -*- coding: utf-8 -*-
"""
芯片产品作战看板 - Chip Product Dashboard
KR 的芯片自动化工作流指挥中心

功能:
1. PDF 规格书上传与解析
2. 1688 上架监控
3. 销售数据可视化
4. 团队任务管理
5. 自动化流程追踪

作者：KR + Claude Code
日期：2026-03-22
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
import os
import json
import re
import sys
import importlib
from pathlib import Path

# 导入项目根目录，支持 scripts 和 dashboard 包的导入
project_root = Path(__file__).parent.parent
scripts_path = project_root / "scripts"
sys.path.insert(0, str(scripts_path))
from database import (
    init_database,
    ProductManager,
    DetailPageManager,
    UploadQueueManager,
    SeriesManager,
    SolutionManager,
    SolutionDocumentManager,
    CustomerManager,
    DistributionManager,
    PartnerCompanyManager,
    ensure_database_initialized
)
from platform_distribution import PlatformManager

# ==================== 1688 产品详情页生成器 ====================
class ProductDetailGenerator:
    """1688 产品详情页生成器"""

    def __init__(self, product_data: dict):
        self.product = product_data
        self.model = product_data.get('型号', 'N/A')
        self.name = product_data.get('品名', '芯片产品')
        self.brand = product_data.get('品牌', '冠辰科技')
        self.category = product_data.get('分类', 'LED 驱动芯片')

    def generate_html(self) -> str:
        """生成 HTML 格式详情页"""
        efficiency = self.product.get('效率', '')
        frequency = self.product.get('开关频率', '')
        accuracy = self.product.get('电流精度', '')
        protection = self.product.get('保护功能', '过流保护/过温保护')

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{self.name} - {self.model}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #ff6a00, #ff9900); color: white; padding: 40px 20px; text-align: center; }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .section {{ background: white; margin: 20px 0; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .section-title {{ font-size: 24px; color: #ff6a00; border-left: 4px solid #ff6a00; padding-left: 15px; margin-bottom: 20px; }}
        .param-table {{ width: 100%; border-collapse: collapse; }}
        .param-table th, .param-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        .param-table th {{ background: #f9f9f9; font-weight: 600; width: 30%; }}
        .highlight {{ color: #ff6a00; font-weight: 600; }}
        .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }}
        .feature-card {{ background: linear-gradient(135deg, #fff5eb, #ffffff); padding: 20px; border-radius: 8px; border-left: 3px solid #ff6a00; }}
        .feature-card h3 {{ color: #333; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.name}</h1>
        <div style="font-size: 24px; margin-top: 10px;">型号：{self.model}</div>
        <div style="margin-top: 15px; font-size: 18px;">{self.brand} | {self.category}</div>
    </div>
    <div class="container">
        <div class="section">
            <h2 class="section-title">✨ 产品亮点</h2>
            <div class="features">
                {f'<div class="feature-card"><h3>⚡ 高效率</h3><p>转换效率高达 <span class="highlight">{efficiency}</span></p></div>' if efficiency else ''}
                {f'<div class="feature-card"><h3>📡 高频工作</h3><p>开关频率 <span class="highlight">{frequency}</span></p></div>' if frequency else ''}
                {f'<div class="feature-card"><h3>🎯 高精度</h3><p>电流精度 <span class="highlight">{accuracy}</span></p></div>' if accuracy else ''}
                <div class="feature-card"><h3>🛡️ 完善保护</h3><p>{protection}</p></div>
                <div class="feature-card"><h3>🔧 易用设计</h3><p>外围电路简单，支持快速开发</p></div>
            </div>
        </div>
        <div class="section">
            <h2 class="section-title">⚙️ 技术参数</h2>
            <table class="param-table">
                <tr><th>产品型号</th><td>{self.model}</td></tr>
                <tr><th>产品名称</th><td>{self.name}</td></tr>
                <tr><th>品牌</th><td>{self.brand}</td></tr>
                <tr><th>输入电压</th><td>{self.product.get('输入电压', 'N/A')}</td></tr>
                <tr><th>输出电压</th><td>{self.product.get('输出电压', 'N/A')}</td></tr>
                <tr><th>输出电流</th><td>{self.product.get('输出电流', 'N/A')}</td></tr>
                <tr><th>效率</th><td>{self.product.get('效率', 'N/A')}</td></tr>
                <tr><th>开关频率</th><td>{self.product.get('开关频率', 'N/A')}</td></tr>
                <tr><th>电流精度</th><td>{self.product.get('电流精度', 'N/A')}</td></tr>
                <tr><th>工作温度</th><td>{self.product.get('工作温度', 'N/A')}</td></tr>
                <tr><th>封装形式</th><td>{self.product.get('封装形式', 'N/A')}</td></tr>
                <tr><th>保护功能</th><td>{self.product.get('保护功能', 'N/A')}</td></tr>
            </table>
        </div>
        <div class="section">
            <h2 class="section-title">🎯 应用领域</h2>
            <ul style="list-style: none; line-height: 2;">
                <li>✓ 室内照明：筒灯、射灯、面板灯、吸顶灯</li>
                <li>✓ 商业照明：轨道灯、格栅灯、吊灯</li>
                <li>✓ 装饰照明：灯带、线条灯、点光源</li>
                <li>✓ 智能照明：可调光调色驱动系统</li>
                <li>✓ 工业照明：工矿灯、投光灯、路灯</li>
            </ul>
        </div>
        <div class="section">
            <h2 class="section-title">📦 包装信息</h2>
            <table class="param-table">
                <tr><th>包装方式</th><td>卷带包装 (Tape & Reel)</td></tr>
                <tr><th>最小起订量</th><td>100 pcs</td></tr>
                <tr><th>供货能力</th><td>100,000 pcs/周</td></tr>
                <tr><th>交货周期</th><td>现货 / 3-5 天</td></tr>
            </table>
        </div>
        <div class="footer" style="text-align: center; padding: 30px; color: #999;">
            <p>© 2026 冠辰科技 版权所有</p>
        </div>
    </div>
</body>
</html>"""
        return html

    def generate_markdown(self) -> str:
        """生成 Markdown 格式详情页"""
        efficiency = self.product.get('效率', '')
        frequency = self.product.get('开关频率', '')
        accuracy = self.product.get('电流精度', '')

        features = []
        if efficiency:
            features.append(f"- **⚡ 高效率**: 转换效率高达 {efficiency}")
        if frequency:
            features.append(f"- **📡 高频工作**: 开关频率 {frequency}")
        if accuracy:
            features.append(f"- **🎯 高精度**: 电流精度 {accuracy}")
        features.append("- **🛡️ 完善保护**: 多重保护功能")
        features.append("- **🔧 易用设计**: 外围电路简单")

        md = f"""# {self.name} - {self.model}

**品牌**: {self.brand} | **分类**: {self.category}

---

## ✨ 产品亮点

{chr(10).join(features)}

---

## ⚙️ 技术参数

| 参数名称 | 规格值 |
|----------|--------|
| 产品型号 | {self.model} |
| 产品名称 | {self.name} |
| 输入电压 | {self.product.get('输入电压', 'N/A')} |
| 输出电压 | {self.product.get('输出电压', 'N/A')} |
| 输出电流 | {self.product.get('输出电流', 'N/A')} |
| 效率 | {self.product.get('效率', 'N/A')} |
| 开关频率 | {self.product.get('开关频率', 'N/A')} |
| 电流精度 | {self.product.get('电流精度', 'N/A')} |
| 工作温度 | {self.product.get('工作温度', 'N/A')} |
| 封装形式 | {self.product.get('封装形式', 'N/A')} |

---

## 🎯 应用领域

- 室内照明：筒灯、射灯、面板灯、吸顶灯
- 商业照明：轨道灯、格栅灯、吊灯
- 装饰照明：灯带、线条灯、点光源
- 智能照明：可调光调色驱动系统
- 工业照明：工矿灯、投光灯、路灯

---

## 📦 包装信息

| 项目 | 规格 |
|------|------|
| 包装方式 | 卷带包装 (Tape & Reel) |
| 最小起订量 | 100 pcs |
| 供货能力 | 100,000 pcs/周 |
| 交货周期 | 现货 / 3-5 天 |

---

© 2026 冠辰科技 版权所有
"""
        return md

# ==================== 全局变量初始化 ====================
if 'edit_product_index' not in st.session_state:
    st.session_state.edit_product_index = None
if 'view_product_index' not in st.session_state:
    st.session_state.view_product_index = None

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="芯片产品作战看板 | KR 的指挥中心",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 自定义 CSS 样式 ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        padding: 1rem 0;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .status-success { background-color: #10b981; color: white; }
    .status-warning { background-color: #f59e0b; color: white; }
    .status-danger { background-color: #ef4444; color: white; }
    .status-info { background-color: #3b82f6; color: white; }
</style>
""", unsafe_allow_html=True)

# ==================== 对话框函数 ====================
# 注意：这些函数必须在调用之前定义！

@st.dialog("✏️ 编辑产品信息")
def edit_product_dialog(product_index):
    """编辑产品信息的对话框"""
    if product_index is None or product_index >= len(st.session_state.products):
        st.error("无效的产品索引")
        return

    product = st.session_state.products[product_index]

    st.markdown(f"### 编辑：**{product.get('型号', 'N/A')}**")
    st.info("修改完成后点击保存，数据将同步到产品库")

    # 使用表单收集编辑数据
    with st.form("edit_product_form"):
        col1, col2 = st.columns(2)

        with col1:
            edited_model = st.text_input("️ 型号", value=product.get('型号', ''))
            edited_name = st.text_input("📦 产品名称", value=product.get('名称', ''))
            edited_voltage = st.text_input("⚡ 电压", value=str(product.get('电压', '')))
            edited_power = st.text_input("💡 功率", value=str(product.get('功率', '')))

        with col2:
            edited_package = st.text_input("📦 封装类型", value=str(product.get('封装', '')))
            edited_temp = st.text_input("🌡️ 工作温度", value=str(product.get('温度', '')))
            edited_cost = st.text_input("💰 成本", value=str(product.get('成本', '')))
            edited_price = st.text_input("💵 建议售价", value=str(product.get('建议售价', '')))

        # 提交按钮
        submitted = st.form_submit_button("💾 保存修改", type="primary", use_container_width=True)

        if submitted:
            # 更新产品数据
            st.session_state.products[product_index].update({
                '型号': edited_model,
                '名称': edited_name,
                '电压': edited_voltage,
                '功率': edited_power,
                '封装': edited_package,
                '温度': edited_temp,
                '成本': edited_cost,
                '建议售价': edited_price
            })

            # 同步更新到数据库
            product_id = product.get('id')
            if product_id:
                update_data = {
                    '型号': edited_model,
                    '名称': edited_name,
                    '输入电压': edited_voltage,
                    '输出电流': edited_power,
                    '封装形式': edited_package,
                    '工作温度': edited_temp,
                    '成本': edited_cost,
                    '建议售价': edited_price
                }
                ProductManager.update_product(product_id, update_data)

            st.success("✅ 产品信息已更新（已同步到数据库）！")
            st.balloons()
            st.rerun()

@st.dialog("📊 产品详细数据")
def view_product_detail_dialog(product_index):
    """查看产品详细数据的对话框"""
    if product_index is None or product_index >= len(st.session_state.products):
        st.error("无效的产品索引")
        return

    product = st.session_state.products[product_index]

    st.markdown(f"### 📊 **{product.get('型号', 'N/A')}** - 详细数据")

    # 基本信息卡片
    st.subheader("📋 基本信息")
    info_col1, info_col2, info_col3 = st.columns(3)

    with info_col1:
        st.metric("型号", product.get('型号', 'N/A'))
        st.metric("电压", product.get('电压', 'N/A'))
        st.metric("封装", product.get('封装', 'N/A'))

    with info_col2:
        st.metric("产品名称", product.get('名称', 'N/A'))
        st.metric("功率", product.get('功率', 'N/A'))
        st.metric("工作温度", product.get('温度', 'N/A'))

    with info_col3:
        st.metric("成本", product.get('成本', 'N/A'))
        st.metric("建议售价", product.get('建议售价', 'N/A'))
        profit = "N/A"
        if product.get('成本') and product.get('建议售价'):
            try:
                cost_str = str(product.get('成本')).replace('¥', '').replace('元', '').strip()
                price_str = str(product.get('建议售价')).replace('¥', '').replace('元', '').strip()
                # 简单处理范围值，取中间值
                if '-' in cost_str:
                    cost_val = float(cost_str.split('-')[0].strip())
                else:
                    cost_val = float(cost_str)
                if '-' in price_str:
                    price_val = float(price_str.split('-')[0].strip())
                else:
                    price_val = float(price_str)
                profit = f"¥{price_val - cost_val:.2f}"
            except:
                profit = "计算失败"
        st.metric("预估利润", profit)

    st.divider()

    # 原始数据（如果有）
    st.subheader("📄 原始解析数据")
    st.json(product)

    # 可视化图表
    st.divider()
    st.subheader("📈 价格分析")

    # 简单的成本 vs 售价对比图
    if product.get('成本') and product.get('建议售价'):
        try:
            cost_str = str(product.get('成本')).replace('¥', '').replace('元', '').strip()
            price_str = str(product.get('建议售价')).replace('¥', '').replace('元', '').strip()

            if '-' in cost_str:
                cost_low, cost_high = map(float, cost_str.split('-'))
            else:
                cost_low = cost_high = float(cost_str)

            if '-' in price_str:
                price_low, price_high = map(float, price_str.split('-'))
            else:
                price_low = price_high = float(price_str)

            chart_data = pd.DataFrame({
                '类型': ['成本', '售价'],
                '最低': [cost_low, price_low],
                '最高': [cost_high, price_high]
            })

            fig = px.bar(chart_data, x='类型', y=['最低', '最高'],
                        title='成本 vs 售价对比',
                        barmode='group',
                        color_discrete_sequence=['#ef4444', '#22c55e'])
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("图表生成失败，请检查数据格式")

# ==================== PDF 解析函数 ====================
def parse_chip_pdf(file_path):
    """
    解析芯片 PDF 规格书，提取关键字段
    返回产品列表
    """
    products = []

    try:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        full_text = ""
        first_page_text = ""

        # 提取所有页面文本
        for i, page in enumerate(doc):
            page_text = page.get_text()
            full_text += page_text
            if i == 0:
                first_page_text = page_text

        doc.close()

        # ==================== 智能提取型号 ====================
        model_number = "未知型号"

        # 策略 1: 从文件名提取 (最可靠)
        import os
        filename = os.path.basename(file_path)
        # 匹配 SM8645SG、SM8640SGA 等格式
        fname_model = re.search(r'([A-Z]{2,}\d+[A-Z]{0,3})', filename.replace('.pdf', '').replace('_', ''))
        if fname_model:
            model_number = fname_model.group(1)

        # 策略 2: 从 PDF 第一页提取（型号通常在标题位置）
        if model_number == "未知型号":
            # 查找大字号的型号标识（通常是文档中最大的文本）
            lines = first_page_text.split('\n')
            for line in lines[:20]:  # 检查前 20 行
                line = line.strip()
                # 匹配类似 SM8645SG、SM8640SGA 格式
                model_match = re.search(r'([A-Z]{2,}\d+[A-Z]{1,3})', line)
                if model_match:
                    model_number = model_match.group(1)
                    break

        # 策略 3: 全文搜索型号关键字
        if model_number == "未知型号":
            patterns = [
                r'SM\d+[A-Z]{1,3}',  # SM 系列
                r'[A-Z]{2,}\d+SG[A-Z]?',  # xxSG 系列
                r'Part\s*(?:No\.?)?[:\s]*([A-Za-z0-9\-]+)',
                r'型号\s*[:\s]*([A-Za-z0-9\-]+)',
                r'Model\s*[:\s]*([A-Za-z0-9\-]+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    model_number = match.group(1) if match.group(1) else match.group(0)
                    break

        # ==================== 提取产品名称 ====================
        product_name = "未命名产品"
        name_patterns = [
            r'(?:产品名称 | Description|Product\s*Name)[:\s]*([^\n]+)',
            r'描述\s*[:\s]*([^\n]+)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                product_name = match.group(1).strip()
                break

        # 如果没有找到描述，用型号作为名称
        if product_name == "未命名产品" and model_number != "未知型号":
            product_name = f"{model_number} 芯片"

        # ==================== 提取电压参数 ====================
        voltage = "未知"
        voltage_patterns = [
            r'([VＶ][\s\.]?[Cc]?[CdD]?[:\s]?[\d\.]+\s*[VvV](?:\s*[-~至～]\s*[\d\.]+\s*[VvV])?)',
            r'([VvV][\s]?[Cc]?[DdD]?[:\s]?[\d\.]+(?:\s*[-~至～]\s*[\d\.]+)?\s*[VvV]?)',
            r'电压\s*[:\s]?([\d\.]+\s*V(?:\s*[-~至～]\s*[\d\.]+\s*V)?)',
            r'Vcc\s*[:\s]?([\d\.]+\s*V)',
            r'Vdd\s*[:\s]?([\d\.]+\s*V)',
        ]
        for pattern in voltage_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                voltage = match.group(1).strip()
                break

        # ==================== 提取功率参数 ====================
        power = "未知"
        power_patterns = [
            r'功率\s*[:\s]?([\d\.]+\s*W)',
            r'功耗\s*[:\s]?([\d\.]+\s*W)',
            r'Power\s*[:\s]?([\d\.]+\s*W)',
            r'([Dd]issipation)[:\s]?([\d\.]+\s*W)',
        ]
        for pattern in power_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                power = match.group(2) if match.group(2) else match.group(1)
                break

        # ==================== 提取封装类型 ====================
        package = "未知"
        package_patterns = [
            r'封装\s*[:\s]?([A-Z]{2,}\-?\d+)',
            r'Package\s*[:\s]?([A-Z]{2,}\-?\d+)',
            r'SOP\-?\d+',
            r'DIP\-?\d+',
            r'SSOP\-?\d+',
        ]
        for pattern in package_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                package = match.group(0)
                break

        # ==================== 提取工作温度 ====================
        temp_range = "未知"
        temp_patterns = [
            r'温度\s*[:\s]?(-?\d+\s*°?[CF]?\s*[~\-至～]\s*-?\d+\s*°?[CF]?)',
            r'Temperature\s*[:\s]?(-?\d+\s*°?[CF]?\s*[~\-]\s*-?\d+\s*°?[CF]?)',
            r'(-?\d+°?[CF]\s*[~\-至～]\s*-?\d+°?[CF])',
        ]
        for pattern in temp_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                temp_range = match.group(1)
                break

        # ==================== 计算成本和售价（临时逻辑） ====================
        cost = "待核算"
        price = "待定价"

        # 根据市场常见芯片价格估算（临时）
        if model_number != "未知型号":
            cost = "￥0.5-2.0 (估算)"
            price = "￥2.5-8.0 (建议)"

        products.append({
            '型号': model_number,
            '名称': product_name,
            '电压': voltage,
            '功率': power,
            '封装': package,
            '温度': temp_range,
            '成本': cost,
            '建议售价': price
        })

    except ImportError:
        st.error("❌ 未安装 PyMuPDF，请运行：pip install pymupdf")
        return []
    except Exception as e:
        st.error(f"❌ 解析失败：{str(e)}")
        return []

    return products

# ==================== 初始化 Session State 和数据库 ====================
# 初始化数据库
ensure_database_initialized()
init_database()

if 'products' not in st.session_state:
    # 从数据库加载产品
    db_products = ProductManager.get_all_products()
    # 状态映射：数据库英文 -> 中文显示
    status_map = {'active': '已上架', 'pending': '待上架', 'reviewing': '审核中', 'offline': '已下架'}
    # 转换格式，兼容现有代码
    st.session_state.products = []
    for prod in db_products:
        db_status = prod.get('status', 'pending')
        st.session_state.products.append({
            'id': prod.get('id'),
            '型号': prod.get('model', ''),
            '名称': prod.get('name', ''),
            '品牌': prod.get('brand', '冠辰科技'),
            '分类': prod.get('category', 'LED 驱动芯片'),
            '电压': prod.get('input_voltage', 'N/A'),
            '功率': prod.get('output_current', 'N/A'),
            '成本': prod.get('cost', 0),
            '建议售价': prod.get('suggested_price', 0),
            'status': status_map.get(db_status, db_status),  # 转换为中文状态
            'pdf_path': prod.get('pdf_file_path', '')
        })

if 'tasks' not in st.session_state:
    st.session_state.tasks = []
# parsed_data 只在明确需要时设置，不在初始化时重置

# ==================== 侧边栏 ====================
with st.sidebar:
    # 显示 KONGSON 冠辰 LOGO - 居中并适配大小
    logo_path = os.path.join(os.path.dirname(__file__), "kongson_logo.jpg")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.image("https://img.icons8.com/color/96/chip.png", width=80)

    st.title("🎯 作战指挥中心")
    st.markdown("**指挥官：** KR (任光成)")
    st.markdown("**最后更新：** " + datetime.now().strftime("%Y-%m-%d %H:%M"))

    st.divider()

    # 导航菜单
    menu = st.radio(
        "📋 导航菜单",
        ["📊 总览看板",
         "🏢 品牌与系列",
         "💡 方案开发服务",
         "👥 客户管理",
         "🏭 关联公司数据",
         "📄 PDF 规格书解析",
         "🛒 1688 上架监控",
         "💰 销售数据",
         "👥 团队任务",
         "📱 公众号发布",
         "⚙️ 自动化流程"],
        label_visibility="collapsed"
    )

    st.divider()

    # 快速统计
    st.subheader("📈 实时数据")
    total_products = len(st.session_state.products)
    st.metric("产品总数", total_products)

    if st.session_state.tasks:
        completed = sum(1 for t in st.session_state.tasks if t.get('status') == '已完成')
        st.metric("任务完成率", f"{completed}/{len(st.session_state.tasks)}")

# ==================== 主标题 ====================
# 显示主标题和 LOGO
logo_col, title_col = st.columns([1, 4])

with logo_col:
    logo_path_main = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "冠辰 - 国高 + 中英文商标.jpg")
    if os.path.exists(logo_path_main):
        st.image(logo_path_main, width=200)

with title_col:
    st.markdown('<p class="main-header">🎯 芯片产品作战看板</p>', unsafe_allow_html=True)

st.markdown("---")

# ==================== 页面 1: 总览看板 ====================
if menu == "📊 总览看板":
    st.header("今日作战态势")

    # KPI 卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📦 产品总数",
            value=len(st.session_state.products),
            delta="+2 本周"
        )

    with col2:
        st.metric(
            label="🛒 1688 上架",
            value=sum(1 for p in st.session_state.products if p.get('status') == '已上架'),
            delta="待上架：" + str(sum(1 for p in st.session_state.products if p.get('status') == '待上架'))
        )

    with col3:
        st.metric(
            label="💰 今日销售额",
            value="¥0",
            delta="数据待同步"
        )

    with col4:
        st.metric(
            label="👥 团队在线",
            value="4 人",
            delta="中山 2 + 华强北 1 + 宁波 1"
        )

    st.divider()

    # 产品状态分布
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 产品状态分布")
        # 状态映射：数据库英文状态 -> 中文显示
        status_map = {
            'active': '已上架',
            'pending': '待上架',
            'reviewing': '审核中',
            'offline': '已下架'
        }
        # 统计各状态数量
        status_counts = {'已上架': 0, '待上架': 0, '审核中': 0, '已下架': 0}
        for p in st.session_state.products:
            db_status = p.get('status', 'pending')
            # 如果是数据库中的英文状态，转换为中文
            if db_status in status_map:
                cn_status = status_map[db_status]
            else:
                # 如果已经是中文，直接使用
                cn_status = db_status if db_status in status_counts else '待上架'
            if cn_status in status_counts:
                status_counts[cn_status] += 1

        status_data = pd.DataFrame({
            '状态': list(status_counts.keys()),
            '数量': list(status_counts.values())
        })

        if status_data['数量'].sum() > 0:
            fig = px.pie(status_data, values='数量', names='状态',
                        color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无产品数据，请上传 PDF 规格书")

    with col2:
        st.subheader("📈 周销售趋势（示例）")
        dates = pd.date_range(start='2026-03-16', periods=7)
        sales_data = pd.DataFrame({
            '日期': dates,
            '销售额': [1200, 1500, 1800, 2100, 1900, 2500, 2800],
            '订单数': [12, 15, 18, 21, 19, 25, 28]
        })

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sales_data['日期'], y=sales_data['销售额'],
                                name='销售额', line=dict(color='#667eea')))
        fig.add_trace(go.Scatter(x=sales_data['日期'], y=sales_data['订单数'] * 100,
                                name='订单数 (x100)', line=dict(color='#f59e0b')))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 最近活动
    st.subheader("📝 最近活动")
    st.info("""
    - **17:00** - KR 启动了芯片自动化工作流项目
    - **16:45** - PDF 解析工具部署完成
    - **16:30** - Streamlit 看板环境配置成功
    - **16:00** - 项目初始化完成
    """)

# ==================== 页面 2: 品牌与系列管理 ====================
elif menu == "🏢 品牌与系列":
    st.header("🏢 品牌与系列管理")
    st.markdown("管理芯片品牌和产品系列，实现批量操作和分类展示")

    st.divider()

    # 选项卡：品牌管理 | 系列管理 | 批量操作
    tab1, tab2, tab3 = st.tabs(["🏷️ 品牌管理", "📦 系列管理", "⚡ 批量操作"])

    # ========== 选项卡 1: 品牌管理 ==========
    with tab1:
        st.subheader("🏷️ 品牌管理")

        # 添加新品牌
        col1, col2 = st.columns([2, 1])
        with col1:
            new_brand = st.text_input(
                "添加新品牌",
                placeholder="如：士兰微、晶丰明源、矹力杰、TI、MPS...",
                key="new_brand_input"
            )
        with col2:
            if st.button("➕ 添加品牌", key="add_brand_btn"):
                if new_brand:
                    # 创建一个默认系列
                    SeriesManager.add_series(new_brand, f"{new_brand}系列")
                    st.success(f"✅ 品牌 '{new_brand}' 添加成功！")
                    st.rerun()

        st.divider()

        # 品牌列表
        st.subheader("📋 现有品牌")
        all_series = SeriesManager.get_all_series()
        brands = list(set(s['brand'] for s in all_series))

        if brands:
            for brand in brands:
                brand_series = [s for s in all_series if s['brand'] == brand]
                with st.expander(f"**🏢 {brand}** ({len(brand_series)} 个系列)"):
                    for series in brand_series:
                        st.write(f"- 📦 **{series['series_name']}** - {series.get('description', '暂无描述')}")
        else:
            st.info("暂无品牌，请添加")

    # ========== 选项卡 2: 系列管理 ==========
    with tab2:
        st.subheader("📦 系列管理")

        # 添加新系列
        st.markdown("**添加新系列**")
        col1, col2, col3 = st.columns(3)
        with col1:
            series_brand = st.selectbox(
                "选择品牌",
                options=brands if brands else ["请先添加品牌"],
                key="series_brand_select"
            )
        with col2:
            series_name = st.text_input("系列名称", placeholder="如：SM89 系列", key="series_name_input")
        with col3:
            series_desc = st.text_input("系列描述（可选）", placeholder="如：高性能 LED 驱动芯片", key="series_desc_input")

        if st.button("➕ 添加系列", key="add_series_btn"):
            if series_brand and series_name and series_brand != "请先添加品牌":
                SeriesManager.add_series(series_brand, series_name, series_desc if series_desc else None)
                st.success(f"✅ 系列 '{series_name}' 添加成功！")
                st.rerun()

        st.divider()

        # 系列列表
        st.subheader("📋 现有系列")
        if all_series:
            # 按品牌分组显示
            for brand in brands:
                brand_series_list = [s for s in all_series if s['brand'] == brand]
                if brand_series_list:
                    st.markdown(f"**🏢 {brand}**")
                    for series in brand_series_list:
                        # 获取该系列下的产品数量
                        series_products = ProductManager.get_products_by_series(series_id=series['id'])
                        product_count = len(series_products)

                        col_series, col_products, col_action = st.columns([3, 1, 1])
                        with col_series:
                            st.write(f"📦 **{series['series_name']}** - {series.get('description', '暂无描述')}")
                        with col_products:
                            st.metric("产品数", product_count)
                        with col_action:
                            if st.button("🗑️ 删除", key=f"del_series_{series['id']}"):
                                SeriesManager.delete_series(series['id'])
                                st.success("✅ 系列已删除")
                                st.rerun()
                    st.divider()
        else:
            st.info("暂无系列，请添加")

    # ========== 选项卡 3: 批量操作 ==========
    with tab3:
        st.subheader("⚡ 批量操作")
        st.info("💡 提示：在产品列表页面可以进行批量上架、批量删除等操作")

        # 按系列统计
        st.subheader("📊 系列统计")
        if all_series:
            series_stats = []
            for series in all_series:
                products = ProductManager.get_products_by_series(series_id=series['id'])
                active_count = len(products)
                series_stats.append({
                    '品牌': series['brand'],
                    '系列': series['series_name'],
                    '产品数量': active_count
                })

            stats_df = pd.DataFrame(series_stats)
            st.dataframe(stats_df, use_container_width=True)
        else:
            st.info("暂无系列数据")

# ==================== 页面 3: 方案开发服务 ====================
elif menu == "💡 方案开发服务":
    st.header("💡 冠辰科技方案开发服务")
    st.markdown("管理智能照明、电源电池、传感感应、电机风扇四大领域的产品方案")

    # 领域定义
    DOMAINS = ["智能照明", "电源电池", "传感感应", "电机风扇"]
    DOMAIN_ICONS = {
        "智能照明": "💡",
        "电源电池": "🔋",
        "传感感应": "📡",
        "电机风扇": "🌀"
    }

    # 子分类定义
    SUB_DOMAINS = {
        "智能照明": ["LED 驱动", "调光调色", "智能控制", "线性照明", "商业照明"],
        "电源电池": ["电源管理", "BMS 电池管理", "充电方案", "DC-DC 转换", "适配器"],
        "传感感应": ["传感器接口", "信号处理", "检测模块", "智能传感", "工业传感"],
        "电机风扇": ["电机驱动", "风速控制", "静音技术", "BLDC 控制", "伺服控制"]
    }

    # 选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["📚 方案库", "➕ 添加方案", "📊 统计看板", "📁 文档管理"])

    # ========== 选项卡 1: 方案库 ==========
    with tab1:
        st.subheader("📚 方案库")

        # 筛选器
        col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 1])
        with col_filter1:
            selected_domain = st.selectbox("🔍 选择领域", ["全部"] + DOMAINS, key="domain_filter")
        with col_filter2:
            selected_status = st.selectbox("状态", ["全部", "开发中", "已发布", "已停产"], key="status_filter")
        with col_filter3:
            search_text = st.text_input("🔎 搜索", placeholder="方案名称/芯片", key="solution_search")

        # 获取方案
        domain_filter = selected_domain if selected_domain != "全部" else None
        status_filter = selected_status if selected_status != "全部" else None
        all_solutions = SolutionManager.get_all_solutions(domain=domain_filter, status=status_filter)

        # 搜索过滤
        if search_text:
            all_solutions = [s for s in all_solutions if
                           search_text.lower() in s['solution_name'].lower() or
                           search_text.lower() in (s.get('core_chip') or '').lower()]

        # 显示方案
        if all_solutions:
            for solution in all_solutions:
                with st.expander(f"{DOMAIN_ICONS.get(solution['domain'], '💡')} {solution['solution_name']} - {solution.get('core_chip', 'N/A')}", expanded=False):
                    # 基本信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**🏷️ 领域:** {solution['domain']}")
                        st.markdown(f"**📂 子分类:** {solution.get('sub_domain', 'N/A')}")
                        st.markdown(f"**💼 应用:** {solution.get('application', 'N/A')}")
                    with col2:
                        st.markdown(f"**📄 类型:** {solution.get('solution_type', '标准方案')}")
                        st.markdown(f"**🔧 状态:** {solution.get('status', '开发中')}")
                        st.markdown(f"**💾 芯片:** {solution.get('core_chip', 'N/A')}")
                    with col3:
                        st.markdown(f"**📅 创建:** {solution.get('created_at', 'N/A')[:10]}")

                    st.divider()

                    # 方案特点
                    if solution.get('features'):
                        st.markdown("**✨ 方案特点:**")
                        st.info(solution.get('features'))

                    # 方案描述
                    if solution.get('description'):
                        st.markdown("**📝 方案描述:**")
                        st.write(solution.get('description'))

                    # 关联文档
                    st.divider()
                    st.markdown("**📎 关联文档:**")
                    docs = SolutionDocumentManager.get_documents_by_solution(solution['id'])
                    if docs:
                        doc_cols = st.columns(len(docs) + 1)
                        for i, doc in enumerate(docs):
                            with doc_cols[i]:
                                st.download_button(
                                    label=f"📄 {doc['doc_name']} ({doc['doc_type']})",
                                    data=open(doc['file_path'], 'rb') if os.path.exists(doc['file_path']) else b'',
                                    file_name=doc['doc_name'],
                                    key=f"download_{doc['id']}"
                                )
                    else:
                        st.caption("暂无关联文档")

                    # 操作按钮
                    st.divider()
                    action_col1, action_col2 = st.columns([3, 1])
                    with action_col1:
                        # 客户分发
                        customers = CustomerManager.get_all_customers()
                        if customers:
                            customer_options = {f"{c['company_name']} ({c['contact_person']})": c['id'] for c in customers}
                            selected_customer = st.selectbox(
                                "📤 分发给客户",
                                [""] + list(customer_options.keys()),
                                key=f"dist_{solution['id']}"
                            )
                            if selected_customer and st.button("发送方案", key=f"send_{solution['id']}"):
                                DistributionManager.add_distribution(
                                    solution['id'],
                                    customer_options[selected_customer],
                                    distributed_by="KR"
                                )
                                st.success(f"✅ 方案已发送给 {selected_customer}")
                                st.rerun()
                    with action_col2:
                        if st.button("🗑️ 删除方案", key=f"del_sol_{solution['id']}"):
                            SolutionManager.delete_solution(solution['id'])
                            st.success("✅ 方案已删除")
                            st.rerun()
        else:
            st.info("暂无方案数据，请切换到「添加方案」标签页添加新方案")

    # ========== 选项卡 2: 添加方案 ==========
    with tab2:
        st.subheader("➕ 添加新方案")

        with st.form("add_solution_form"):
            col1, col2 = st.columns(2)

            with col1:
                sol_name = st.text_input("方案名称 *", placeholder="如：SM89 系列智能照明驱动方案")
                selected_domain_add = st.selectbox("所属领域 *", DOMAINS)
                sub_domain_add = st.selectbox("子分类", SUB_DOMAINS[selected_domain_add])
                application = st.text_input("应用领域", placeholder="如：室内照明/商业照明/工业照明")

            with col2:
                sol_type = st.selectbox("方案类型", ["标准方案", "定制方案"])
                core_chip = st.text_input("核心芯片", placeholder="如：SM8920AS")
                status = st.selectbox("状态", ["开发中", "已发布", "已停产"])

            features = st.text_area("方案特点", placeholder="描述方案的核心优势和特点...", height=80)
            description = st.text_area("方案描述", placeholder="详细描述方案的技术特点、应用场景等...", height=120)

            submitted = st.form_submit_button("✅ 添加方案", type="primary", use_container_width=True)

            if submitted and sol_name:
                solution_data = {
                    'solution_name': sol_name,
                    'domain': selected_domain_add,
                    'sub_domain': sub_domain_add,
                    'solution_type': sol_type,
                    'application': application,
                    'core_chip': core_chip,
                    'features': features,
                    'description': description,
                    'status': status
                }
                solution_id = SolutionManager.add_solution(solution_data)
                st.success(f"✅ 方案「{sol_name}」添加成功！")
                st.rerun()
            elif submitted and not sol_name:
                st.error("❌ 请输入方案名称")

    # ========== 选项卡 3: 统计看板 ==========
    with tab3:
        st.subheader("📊 方案统计看板")

        stats = SolutionManager.get_statistics()

        # KPI 卡片
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        total_solutions = sum(stats['by_domain'].values()) if stats['by_domain'] else 0
        published_count = stats['by_status'].get('已发布', 0)
        developing_count = stats['by_status'].get('开发中', 0)

        with kpi_col1:
            st.metric("📚 方案总数", total_solutions)
        with kpi_col2:
            st.metric("✅ 已发布", published_count)
        with kpi_col3:
            st.metric("🔧 开发中", developing_count)
        with kpi_col4:
            st.metric("📁 标准方案", stats['by_type'].get('标准方案', 0))

        st.divider()

        # 按领域分布
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔍 按领域分布")
            if stats['by_domain']:
                domain_df = pd.DataFrame({'领域': list(stats['by_domain'].keys()), '数量': list(stats['by_domain'].values())})
                fig = px.pie(domain_df, values='数量', names='领域', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无数据")

        with col2:
            st.subheader("📄 按状态分布")
            if stats['by_status']:
                status_df = pd.DataFrame({'状态': list(stats['by_status'].keys()), '数量': list(stats['by_status'].values())})
                fig = px.bar(status_df, x='状态', y='数量', color='数量')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无数据")

        st.divider()

        # 分发统计
        dist_stats = DistributionManager.get_distribution_statistics()
        if dist_stats['by_status']:
            st.subheader("📤 分发状态统计")
            dist_df = pd.DataFrame({'状态': list(dist_stats['by_status'].keys()), '数量': list(dist_stats['by_status'].values())})
            st.dataframe(dist_df, use_container_width=True)

    # ========== 选项卡 4: 文档管理 ==========
    with tab4:
        st.subheader("📁 文档管理")

        # 选择方案
        all_solutions = SolutionManager.get_all_solutions()
        solution_options = {s['solution_name']: s['id'] for s in all_solutions}

        if solution_options:
            selected_sol_name = st.selectbox("选择方案", list(solution_options.keys()))
            selected_sol_id = solution_options[selected_sol_name]

            st.divider()

            # 上传文档
            st.markdown("**📤 上传文档**")
            col_up1, col_up2 = st.columns([3, 1])
            with col_up1:
                doc_name = st.text_input("文档名称", placeholder="如：SM8920AS 数据手册")
            with col_up2:
                doc_type = st.selectbox("文档类型", ["PDF", "原理图", "PCB", "CAD", "生产文件", "其他"])

            doc_desc = st.text_area("文档描述", placeholder="简要描述文档内容...")
            uploaded_file = st.file_uploader("选择文件", type=['pdf', 'zip', 'rar', 'doc', 'docx', 'dwg', 'dxf'])

            if st.button("📎 上传文档"):
                if selected_sol_id and doc_name and uploaded_file:
                    # 保存文件
                    upload_dir = Path("data/solution_documents")
                    upload_dir.mkdir(parents=True, exist_ok=True)

                    file_path = upload_dir / f"{selected_sol_id}_{uploaded_file.name}"
                    with open(file_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())

                    # 添加到数据库
                    SolutionDocumentManager.add_document(
                        selected_sol_id,
                        doc_name,
                        doc_type,
                        str(file_path),
                        uploaded_file.size,
                        doc_desc
                    )
                    st.success(f"✅ 文档「{doc_name}」上传成功！")
                    st.rerun()
                elif not selected_sol_id:
                    st.error("请先选择方案")
                elif not doc_name:
                    st.error("请输入文档名称")
                elif not uploaded_file:
                    st.error("请上传文件")

            st.divider()

            # 显示当前方案的文档
            st.markdown("**📋 已上传文档**")
            docs = SolutionDocumentManager.get_documents_by_solution(selected_sol_id)
            if docs:
                for doc in docs:
                    doc_col1, doc_col2, doc_col3 = st.columns([3, 1, 1])
                    with doc_col1:
                        st.markdown(f"**📄 {doc['doc_name']}** ({doc['doc_type']})")
                        st.caption(f"大小：{doc.get('file_size', 0) / 1024:.1f} KB | 上传：{doc.get('uploaded_at', 'N/A')}")
                    with doc_col2:
                        if os.path.exists(doc['file_path']):
                            st.download_button(
                                label="📥 下载",
                                data=open(doc['file_path'], 'rb'),
                                file_name=doc['doc_name'],
                                key=f"down_{doc['id']}"
                            )
                    with doc_col3:
                        if st.button("🗑️", key=f"del_doc_{doc['id']}"):
                            SolutionDocumentManager.delete_document(doc['id'])
                            st.success("✅ 文档已删除")
                            st.rerun()
        else:
            st.info("暂无方案，请先添加方案")

# ==================== 页面 4: 客户管理 ====================
elif menu == "👥 客户管理":
    st.header("👥 客户管理")
    st.markdown("管理客户信息、方案分发记录和跟进状态")

    tab1, tab2, tab3 = st.tabs(["📋 客户列表", "➕ 添加客户", "📤 分发记录"])

    # ========== 选项卡 1: 客户列表 ==========
    with tab1:
        st.subheader("📋 客户列表")

        # 筛选
        customer_type_filter = st.selectbox("客户类型", ["全部", "潜在", "意向", "签约", "VIP"], key="cust_type_filter")

        type_filter = customer_type_filter if customer_type_filter != "全部" else None
        customers = CustomerManager.get_all_customers(type_filter)

        if customers:
            for customer in customers:
                with st.expander(f"🏢 {customer['company_name']} - {customer.get('contact_person', 'N/A')}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**📞 电话:** {customer.get('contact_phone', 'N/A')}")
                        st.markdown(f"**📧 邮箱:** {customer.get('contact_email', 'N/A')}")
                    with col2:
                        st.markdown(f"**💼 行业:** {customer.get('industry', 'N/A')}")
                        st.markdown(f"**📍 地区:** {customer.get('region', 'N/A')}")
                    with col3:
                        st.markdown(f"**⭐ 类型:** {customer.get('customer_type', '潜在')}")
                        st.markdown(f"**📅 创建:** {customer.get('created_at', 'N/A')[:10]}")

                    st.divider()

                    # 偏好领域
                    if customer.get('preferred_domains'):
                        st.markdown("**🎯 偏好领域:**")
                        if isinstance(customer['preferred_domains'], list):
                            st.write(", ".join(customer['preferred_domains']))
                        else:
                            st.write(customer['preferred_domains'])

                    # 备注
                    if customer.get('notes'):
                        st.markdown("**📝 备注:**")
                        st.write(customer.get('notes'))

                    st.divider()

                    # 操作
                    col_action1, col_action2 = st.columns([3, 1])
                    with col_action1:
                        # 查看分发的方案
                        distributions = DistributionManager.get_distributions_by_customer(customer['id'])
                        if distributions:
                            st.markdown(f"**📤 已分发方案:** {len(distributions)} 个")
                            for dist in distributions[:3]:  # 显示最近 3 个
                                st.caption(f"- {dist.get('solution_name', 'N/A')} ({dist.get('status', 'N/A')})")
                    with col_action2:
                        if st.button("🗑️ 删除客户", key=f"del_cust_{customer['id']}"):
                            CustomerManager.delete_customer(customer['id'])
                            st.success("✅ 客户已删除")
                            st.rerun()
        else:
            st.info("暂无客户数据")

    # ========== 选项卡 2: 添加客户 ==========
    with tab2:
        st.subheader("➕ 添加新客户")

        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)

            with col1:
                company_name = st.text_input("公司名称 *", placeholder="如：深圳 XX 科技有限公司")
                contact_person = st.text_input("联系人", placeholder="如：张总")
                contact_phone = st.text_input("联系电话", placeholder="如：13800138000")

            with col2:
                contact_email = st.text_input("联系邮箱", placeholder="如：zhang@company.com")
                industry = st.text_input("所属行业", placeholder="如：照明/家电/汽车")
                region = st.text_input("地区", placeholder="如：深圳/中山/上海")

            customer_type = st.selectbox("客户类型", ["潜在", "意向", "签约", "VIP"])

            st.markdown("**🎯 偏好领域**")
            preferred = st.multiselect(
                "选择感兴趣的领域",
                ["智能照明", "电源电池", "传感感应", "电机风扇"]
            )

            notes = st.text_area("备注", placeholder="其他需要记录的信息...")

            submitted = st.form_submit_button("✅ 添加客户", type="primary", use_container_width=True)

            if submitted and company_name:
                customer_data = {
                    'company_name': company_name,
                    'contact_person': contact_person,
                    'contact_phone': contact_phone,
                    'contact_email': contact_email,
                    'industry': industry,
                    'region': region,
                    'customer_type': customer_type,
                    'preferred_domains': preferred,
                    'notes': notes
                }
                CustomerManager.add_customer(customer_data)
                st.success(f"✅ 客户「{company_name}」添加成功！")
                st.rerun()
            elif submitted and not company_name:
                st.error("❌ 请输入公司名称")

    # ========== 选项卡 3: 分发记录 ==========
    with tab3:
        st.subheader("📤 方案分发记录")

        all_distributions = []
        customers = CustomerManager.get_all_customers()
        for customer in customers:
            dists = DistributionManager.get_distributions_by_customer(customer['id'])
            for dist in dists:
                dist['customer_name'] = customer['company_name']
                all_distributions.append(dist)

        if all_distributions:
            dist_df = pd.DataFrame(all_distributions)
            st.dataframe(
                dist_df[['customer_name', 'solution_name', 'distribution_type', 'status', 'distributed_at']],
                use_container_width=True
            )
        else:
            st.info("暂无分发记录")

# ==================== 页面 5: 关联公司数据对接 ====================
elif menu == "🏭 关联公司数据":
    st.header("🏭 关联公司数据对接")
    st.markdown("**希懋 | 智慧世界 | 宜欧特 | 日银微电子** - 数据接口配置与订单管理")

    # 初始化数据库
    ensure_database_initialized()

    # 标签页
    company_tabs = st.tabs(["🏢 公司配置", "📦 产品数据", "📋 订单管理", "📊 统计报表"])

    with company_tabs[0]:  # 公司配置
        st.subheader("关联公司配置")

        # 新增公司表单
        with st.expander("➕ 新增关联公司", expanded=False):
            with st.form("add_company_form"):
                col1, col2 = st.columns(2)
                with col1:
                    company_name = st.text_input("公司名称 *", placeholder="例如：深圳市希懋科技有限公司")
                    company_code = st.selectbox("公司代码 *", ["XIMAO", "SMARTWORLD", "YOUTO", "SILVER"])
                    contact_person = st.text_input("联系人")
                    contact_phone = st.text_input("联系电话")
                with col2:
                    contact_email = st.text_input("联系邮箱")
                    api_endpoint = st.text_input("API 接口地址", placeholder="https://api.example.com")
                    api_key = st.text_input("API Key")
                    api_secret = st.text_input("API Secret")

                sync_freq = st.selectbox("同步频率", ["hourly", "daily", "weekly"])
                notes = st.text_area("备注")

                submitted = st.form_submit_button("💾 保存配置", type="primary")

                if submitted:
                    if company_name and company_code:
                        company_id = PartnerCompanyManager.add_company({
                            'company_name': company_name,
                            'company_code': company_code,
                            'contact_person': contact_person,
                            'contact_phone': contact_phone,
                            'contact_email': contact_email,
                            'api_endpoint': api_endpoint,
                            'api_key': api_key,
                            'api_secret': api_secret,
                            'data_sync_enabled': True,
                            'sync_frequency': sync_freq,
                            'notes': notes
                        })
                        st.success(f"✅ 公司配置已保存 (ID: {company_id})")
                        st.rerun()
                    else:
                        st.error("请填写公司名称和公司代码")

        st.divider()

        # 显示现有公司列表
        st.subheader("已配置公司")
        companies = PartnerCompanyManager.get_all_companies()

        if companies:
            for company in companies:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"#### {company['company_name']}")
                        st.caption(f"代码：{company['company_code']} | 联系人：{company['contact_person'] or '-'}")
                    with col2:
                        status = "🟢 启用" if company['data_sync_enabled'] else "🔴 禁用"
                        st.write(f"状态：{status}")
                        st.write(f"同步频率：{company['sync_frequency']}")
                        if company.get('last_sync_at'):
                            st.caption(f"最后同步：{company['last_sync_at']}")
                    with col3:
                        if st.button("编辑", key=f"edit_company_{company['id']}"):
                            st.info(f"编辑公司 {company['company_name']} - 功能开发中")
                    st.divider()
        else:
            st.info("暂无配置关联公司")

    with company_tabs[1]:  # 产品数据
        st.subheader("📦 合作公司产品数据")

        # 公司筛选
        companies = PartnerCompanyManager.get_all_companies()
        company_options = {c['company_name']: c['id'] for c in companies}

        if company_options:
            selected_company = st.selectbox("选择公司", list(company_options.keys()))

            if selected_company:
                partner_id = company_options[selected_company]
                products = PartnerCompanyManager.get_partner_products(partner_id=partner_id)

                if products:
                    df = pd.DataFrame(products)
                    st.dataframe(
                        df[['product_name', 'product_category', 'price', 'stock_quantity', 'sync_status', 'updated_at']],
                        use_container_width=True
                    )
                else:
                    st.info(f"暂无 {selected_company} 的产品数据")
        else:
            st.info("请先配置关联公司")

    with company_tabs[2]:  # 订单管理
        st.subheader("📋 合作公司订单管理")

        # 公司筛选
        companies = PartnerCompanyManager.get_all_companies()
        company_options = {c['company_name']: c['id'] for c in companies}

        col1, col2 = st.columns(2)
        with col1:
            selected_company = st.selectbox("选择公司", list(company_options.keys()) if company_options else [])
        with col2:
            date_range = st.date_input("日期范围", value=[])

        if selected_company and company_options:
            partner_id = company_options[selected_company]
            orders = PartnerCompanyManager.get_partner_orders(partner_id=partner_id)

            if orders:
                df = pd.DataFrame(orders)
                st.dataframe(
                    df[['order_number', 'customer_name', 'product_name', 'quantity', 'amount', 'order_date', 'order_status']],
                    use_container_width=True
                )

                # 订单统计
                total_amount = df['amount'].sum() if 'amount' in df.columns else 0
                total_orders = len(df)
                st.metric("订单总额", f"¥{total_amount:,.2f}", f"共 {total_orders} 单")
            else:
                st.info(f"暂无 {selected_company} 的订单记录")
        else:
            st.info("请先配置关联公司")

    with company_tabs[3]:  # 统计报表
        st.subheader("📊 合作公司数据统计")

        stats = PartnerCompanyManager.get_partner_statistics()

        # KPI 卡片
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("合作公司数", f"{stats.get('company_count', 0)} 家")

        with col2:
            st.metric("产品总数", f"{stats.get('product_count', 0)} 个")

        with col3:
            st.metric("本月订单", f"{stats.get('orders_this_month', 0)} 单")

        with col4:
            st.metric("本月销售额", f"¥{stats.get('revenue_this_month', 0):,.2f}")

        st.divider()

        # 按公司统计
        st.subheader("按公司统计")
        by_company = stats.get('by_company', {})

        if by_company:
            for company_name, data in by_company.items():
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{company_name}**")
                with col2:
                    st.write(f"订单：{data.get('orders', 0)} | 销售额：¥{data.get('revenue', 0):,.2f}")
        else:
            st.info("暂无统计数据")

# ==================== 页面 5: PDF 规格书解析 ====================
elif menu == "📄 PDF 规格书解析":
    st.header("📄 PDF 规格书智能解析")

    uploaded_files = st.file_uploader(
        "上传芯片 PDF 规格书（支持批量上传）",
        type=['pdf'],
        help="支持芯片规格书、报价单、产品参数表等，可同时选择多个文件上传",
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"✅ 已选择 {len(uploaded_files)} 个文件")

        # 显示所有已上传文件列表
        st.subheader("📁 文件列表")
        for i, uploaded_file in enumerate(uploaded_files):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{i+1}.** {uploaded_file.name}")
            with col2:
                st.info(f"{uploaded_file.size / 1024:.1f} KB")
            with col3:
                st.caption("待解析")

        st.divider()

        # 解析按钮
        if st.button("🚀 批量解析", type="primary", key="parse_button"):
            with st.spinner(f"正在解析 {len(uploaded_files)} 个 PDF 文件..."):
                # 保存上传的文件到临时目录
                temp_dir = os.path.join(os.path.dirname(__file__), "..", "temp")
                os.makedirs(temp_dir, exist_ok=True)

                all_parsed_products = []
                parsed_files_info = []
                failed_files = []

                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"正在解析 ({i+1}/{len(uploaded_files)}): {uploaded_file.name}")
                    temp_file_path = os.path.join(temp_dir, uploaded_file.name)

                    try:
                        with open(temp_file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # 调用 PDF 解析函数
                        parsed_products = parse_chip_pdf(temp_file_path)

                        if parsed_products:
                            all_parsed_products.extend(parsed_products)
                            parsed_files_info.append({
                                'filename': uploaded_file.name,
                                'count': len(parsed_products),
                                'status': '成功'
                            })
                        else:
                            failed_files.append({
                                'filename': uploaded_file.name,
                                'status': '未提取到数据'
                            })

                        # 清理临时文件
                        try:
                            os.remove(temp_file_path)
                        except:
                            pass
                    except Exception as e:
                        failed_files.append({
                            'filename': uploaded_file.name,
                            'status': f'解析失败：{str(e)}'
                        })

                    # 更新进度条
                    progress_bar.progress((i + 1) / len(uploaded_files))

                status_text.text("解析完成！")

                # 显示解析结果
                if all_parsed_products:
                    st.session_state.parsed_data = {
                        'filenames': [f['filename'] for f in parsed_files_info],
                        'parse_time': datetime.now().isoformat(),
                        'status': '批量解析成功',
                        'products': all_parsed_products,
                        'files_info': parsed_files_info,
                        'failed_files': failed_files
                    }
                    st.success(f"✅ 批量解析完成！从 {len(parsed_files_info)} 个文件中提取了 {len(all_parsed_products)} 个产品")

                    if failed_files:
                        st.warning(f"⚠️ 有 {len(failed_files)} 个文件解析失败或未提取到数据")
                else:
                    st.session_state.parsed_data = None
                    st.warning("⚠️ 所有文件都未能提取到产品数据")

        # 显示解析结果
        if 'parsed_data' in st.session_state and st.session_state.parsed_data:
            st.divider()

            # 显示解析摘要信息
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📁 解析文件数", len(st.session_state.parsed_data.get('filenames', [st.session_state.parsed_data.get('filename', '')])))
            with col2:
                st.metric("📦 提取产品数", len(st.session_state.parsed_data['products']))
            with col3:
                st.metric("✅ 成功率", f"{len(st.session_state.parsed_data.get('files_info', [])) / max(len(st.session_state.parsed_data.get('filenames', [1])), 1) * 100:.0f}%")

            # 显示文件解析详情
            if 'files_info' in st.session_state.parsed_data:
                st.subheader("📄 文件解析详情")
                files_df = pd.DataFrame(st.session_state.parsed_data['files_info'])
                st.dataframe(files_df, use_container_width=True, hide_index=True)

                if st.session_state.parsed_data.get('failed_files'):
                    st.subheader("⚠️ 解析失败的文件")
                    failed_df = pd.DataFrame(st.session_state.parsed_data['failed_files'])
                    st.dataframe(failed_df, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("📦 提取的产品列表")
            df = pd.DataFrame(st.session_state.parsed_data['products'])
            st.dataframe(df, use_container_width=True)

            # 添加到产品库
            if st.button("➕ 添加到产品库", key="add_to_products", type="primary"):
                # 查重：检查哪些产品已存在
                new_products = []
                duplicate_products = []

                for prod in st.session_state.parsed_data['products']:
                    model = prod.get('型号', '')
                    # 检查数据库中是否已存在
                    existing = ProductManager.get_product_by_model(model) if model else None
                    if existing:
                        duplicate_products.append(prod)
                    else:
                        new_products.append(prod)

                # 添加新产品
                added_count = 0
                for prod in new_products:
                    result = ProductManager.add_product(prod)
                    if result > 0:
                        added_count += 1
                        st.session_state.products.append(prod)

                # 显示结果
                if duplicate_products:
                    st.warning(f"⚠️ 发现 {len(duplicate_products)} 个重复产品（已跳过）:")
                    dup_df = pd.DataFrame(duplicate_products)
                    st.dataframe(dup_df, use_container_width=True)

                if added_count > 0:
                    st.success(f"✅ 成功添加 {added_count} 个新产品到产品库（已保存到数据库）")
                elif not duplicate_products:
                    st.info("ℹ️ 没有可添加的产品")

                # 刷新页面显示最新数据
                st.rerun()

    else:
        # 示例数据
        st.markdown("""
        ### 📋 支持的 PDF 类型

        | 类型 | 提取字段 |
        |------|----------|
        | 芯片规格书 | 型号、电压、功率、尺寸、工作温度 |
        | 供应商报价单 | 产品名、单价、MOQ、交期 |
        | 产品参数表 | 规格、认证、包装信息 |

        ### 💡 使用提示

        1. 上传 PDF 后点击"开始解析"
        2. 系统自动提取关键字段
        3. 确认数据后添加到产品库
        4. 一键同步到 1688 上架
        """)

# ==================== 页面 4: 1688 上架监控 ====================
elif menu == "🛒 1688 上架监控":
    st.header("🛒 1688 自动上架监控")

    # 产品筛选功能
    st.subheader("🔍 筛选")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        # 品牌筛选
        all_series = SeriesManager.get_all_series()
        brands = list(set(s['brand'] for s in all_series))
        brand_filter = st.selectbox(
            "选择品牌",
            ["全部"] + brands if brands else ["全部"],
            key="brand_filter_select"
        )

    with filter_col2:
        # 系列筛选
        if brand_filter != "全部" and brands:
            brand_series_list = [s['series_name'] for s in all_series if s['brand'] == brand_filter]
            series_filter = st.selectbox(
                "选择系列",
                ["全部"] + brand_series_list if brand_series_list else ["全部"],
                key="series_filter_select"
            )
        else:
            series_filter = "全部"

    with filter_col3:
        # 状态筛选
        status_filter = st.selectbox(
            "筛选状态",
            ["全部", "待上架", "上架中", "已上架", "审核失败"],
            key="status_filter_select"
        )

    st.divider()

    # 查重和清理功能
    with st.expander("🔍 查重工具", expanded=False):
        st.markdown("**检测并清理数据库中的重复产品**")

        if st.button("🔍 检查重复产品", key="check_duplicates"):
            from collections import Counter
            model_counts = Counter(p.get('型号', '') for p in st.session_state.products if p.get('型号'))
            duplicates = {model: count for model, count in model_counts.items() if count > 1}

            if duplicates:
                st.warning(f"⚠️ 发现 **{len(duplicates)}** 个重复的型号:")
                dup_df = pd.DataFrame([
                    {'型号': model, '重复次数': count}
                    for model, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)
                ])
                st.dataframe(dup_df, use_container_width=True)
                st.info("💡 建议：在数据库中保留每个型号的最新记录，删除其他重复项")
            else:
                st.success("✅ 未发现重复产品！")

        st.divider()
        st.markdown("**说明：** 系统已在添加到产品库时自动查重，防止重复产品入库。")

    st.divider()

    # 批量操作区域
    st.subheader("⚡ 批量操作")

    # 初始化选中状态
    if 'selected_products' not in st.session_state:
        st.session_state.selected_products = []

    batch_col1, batch_col2, batch_col3 = st.columns(3)

    with batch_col1:
        # 按系列批量上架
        if all_series:
            series_options = {f"{s['brand']} - {s['series_name']}": s['id'] for s in all_series}
            selected_series = st.selectbox("选择系列", ["全部"] + list(series_options.keys()))
            if st.button("🚀 批量上架", key="batch_upload"):
                if selected_series != "全部":
                    series_id = series_options[selected_series]
                    products = ProductManager.get_products_by_series(series_id=series_id)
                    for prod in products:
                        if prod.get('id'):
                            UploadQueueManager.add_to_queue(prod['id'], prod['model'])
                    st.success(f"✅ 已将 {len(products)} 个产品添加到上架队列")
                else:
                    # 上架所有待上架产品
                    for prod in st.session_state.products:
                        if prod.get('id') and prod.get('status') == '待上架':
                            UploadQueueManager.add_to_queue(prod['id'], prod.get('型号', 'N/A'))
                    st.success("✅ 已将所有待上架产品添加到队列")

    with batch_col2:
        # 按系列批量删除
        if st.button("🗑️ 批量删除", key="batch_delete"):
            if selected_series != "全部":
                series_id = series_options[selected_series]
                products = ProductManager.get_products_by_series(series_id=series_id)
                product_ids = [p['id'] for p in products if p.get('id')]
                if product_ids:
                    deleted = ProductManager.batch_delete_products(product_ids)
                    # 从 session state 移除
                    st.session_state.products = [
                        p for p in st.session_state.products
                        if p.get('id') not in product_ids
                    ]
                    st.success(f"✅ 已删除 {deleted} 个产品")
                    st.rerun()
            else:
                st.warning("⚠️ 请选择要删除的系列")

    with batch_col3:
        # 导出产品列表
        if st.button("📥 导出 Excel", key="batch_export"):
            if st.session_state.products:
                df = pd.DataFrame(st.session_state.products)
                excel_path = "data/products_export.xlsx"
                df.to_excel(excel_path, index=False)
                st.success(f"✅ 已导出到 {excel_path}")

    st.divider()

    # 产品列表
    st.subheader("📦 产品列表")

    if st.session_state.products:
        for i, product in enumerate(st.session_state.products):
            with st.expander(f"**{product.get('型号', 'N/A')}** - {product.get('名称', '未命名产品')}"):
                col1, col2, col3, col4 = st.columns(4)

                col1.metric("电压", product.get('电压', 'N/A'))
                col2.metric("功率", product.get('功率', 'N/A'))
                col3.metric("成本", product.get('成本', 'N/A'))
                col4.metric("建议售价", product.get('建议售价', 'N/A'))

                # 操作按钮
                btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)

                with btn_col1:
                    if st.button("🚀 一键上架", key=f"upload_{i}"):
                        # 保存到数据库队列
                        product_id = product.get('id')
                        if product_id:
                            UploadQueueManager.add_to_queue(product_id, product.get('型号', 'N/A'))
                        st.success("已添加到上架队列")

                with btn_col2:
                    if st.button("✏️ 编辑信息", key=f"edit_{i}"):
                        st.session_state.edit_product_index = i
                        edit_product_dialog(i)

                with btn_col3:
                    if st.button("📊 查看数据", key=f"view_{i}"):
                        st.session_state.view_product_index = i
                        view_product_detail_dialog(i)

                with btn_col4:
                    if st.button("🗑️ 删除产品", key=f"delete_{i}"):
                        product_id = product.get('id')
                        if product_id:
                            # 从数据库软删除
                            ProductManager.delete_product(product_id)
                        # 从 session state 移除
                        st.session_state.products.pop(i)
                        st.success("✅ 产品已删除（已同步到数据库）")
                        st.rerun()

                with btn_col5:
                    # 检查是否已生成 1688 详情页（优先从数据库读取）
                    model = product.get('型号', 'N/A')
                    product_id = product.get('id')

                    # 尝试从数据库获取最新记录
                    db_record = None
                    if product_id:
                        db_record = DetailPageManager.get_latest_page(product_id)

                    if db_record:
                        html_path = Path(db_record.get('html_path', ''))
                        md_path = Path(db_record.get('md_path', ''))

                        if html_path.exists():
                            st.markdown(f"**📄 已生成文件**:")
                            st.markdown(f"- [🌐 打开 HTML 详情页](file://{html_path.absolute().as_posix()})")
                            if md_path.exists():
                                st.markdown(f"- [📄 查看 Markdown 文件](file://{md_path.absolute().as_posix()})")
                        else:
                            st.warning("⚠️ 数据库有记录但文件已丢失")
                    else:
                        # 回退到文件系统扫描
                        output_dir = Path("output/1688")
                        if output_dir.exists():
                            html_files = list(output_dir.glob(f"{model}*.html"))
                            if html_files:
                                latest_html = max(html_files, key=lambda p: p.stat().st_mtime)
                                latest_md = latest_html.with_suffix('.md')
                                st.markdown(f"**📄 已生成文件**:")
                                st.markdown(f"- [🌐 打开 HTML 详情页](file://{latest_html.absolute().as_posix()})")
                                if latest_md.exists():
                                    st.markdown(f"- [📄 查看 Markdown 文件](file://{latest_md.absolute().as_posix()})")
                            else:
                                st.info("尚未生成 1688 详情页")
                        else:
                            st.info("尚未生成 1688 详情页")
    else:
        st.info("暂无产品，请先上传 PDF 规格书")

    st.divider()

    # 上架队列
    st.subheader("⏳ 上架队列")

    # 从数据库读取上架队列
    pending_items = UploadQueueManager.get_pending_items()
    all_items = UploadQueueManager.get_all_items()

    if pending_items or all_items:
        st.write(f"当前等待上架的产品数量：**{len(pending_items)}**")

        if pending_items:
            st.markdown("### 🔄 待上架")
            for item in pending_items:
                st.info(f"**{item['model']}** - 添加到队列：{item['created_at']}")
        else:
            st.success("✅ 没有待上架的产品")

        if all_items:
            st.markdown("### 📋 历史记录")
            for item in all_items[:10]:  # 只显示最近 10 条
                status_icon = "✅" if item['status'] == 'completed' else "⏳"
                st.markdown(f"{status_icon} **{item['model']}** - {item['status']} - {item['created_at']}")
    else:
        st.info("暂无上架队列")

# ==================== 页面 5: 多平台分发 ====================
elif menu == "🌐 多平台分发":
    st.header("🌐 多平台电商分发管理")

    # 获取平台配置
    platforms = PlatformManager.get_all_platforms()
    enabled_platforms = PlatformManager.get_enabled_platforms()

    # 平台概览
    st.subheader("📊 平台概览")

    platform_cols = st.columns(5)
    for i, platform in enumerate(platforms[:5]):
        with platform_cols[i % 5]:
            status = "✅" if platform['is_enabled'] else "⏸️"
            st.markdown(f"""
            <div style="background: #f9fafb; padding: 0.8rem; border-radius: 0.5rem; text-align: center;">
                <div style="font-size: 1.2rem; font-weight: bold;">{platform['platform_name']}</div>
                <div style="font-size: 0.8rem; color: #6b7280;">{platform['store_name']}</div>
                <div style="font-size: 0.8rem; margin-top: 0.5rem;">{status}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # 平台配置管理
    platform_tabs = st.tabs(["平台配置", "分发任务", "订单管理", "数据统计"])

    with platform_tabs[0]:
        st.subheader("⚙️ 平台配置")

        config_col1, config_col2 = st.columns(2)

        with config_col1:
            st.markdown("#### 国内电商平台")
            for platform in platforms:
                if platform['platform_type'] in ['domestic_wholesale', 'domestic_retail', 'content_commerce', 'secondhand']:
                    with st.expander(f"{platform['platform_name']} - {platform['store_name']}"):
                        st.markdown(f"**类型：** {platform['platform_type']}")
                        st.markdown(f"**状态：** {'✅ 启用' if platform['is_enabled'] else '❌ 禁用'}")

                        new_status = st.toggle(
                            "启用",
                            value=bool(platform['is_enabled']),
                            key=f"toggle_{platform['platform_name']}"
                        )

                        if new_status != bool(platform['is_enabled']):
                            PlatformManager.update_platform_config(
                                platform['platform_name'],
                                is_enabled=1 if new_status else 0
                            )
                            st.success(f"已{'启用' if new_status else '禁用'} {platform['platform_name']}")
                            st.rerun()

        with config_col2:
            st.markdown("#### 跨境电商平台")
            for platform in platforms:
                if platform['platform_type'] == 'cross_border' or platform['platform_name'] == '独立站':
                    with st.expander(f"{platform['platform_name']} - {platform['store_name']}"):
                        st.markdown(f"**类型：** {platform['platform_type']}")
                        st.markdown(f"**状态：** {'✅ 启用' if platform['is_enabled'] else '❌ 禁用'}")

                        new_status = st.toggle(
                            "启用",
                            value=bool(platform['is_enabled']),
                            key=f"toggle_{platform['platform_name']}"
                        )

                        if new_status != bool(platform['is_enabled']):
                            PlatformManager.update_platform_config(
                                platform['platform_name'],
                                is_enabled=1 if new_status else 0
                            )
                            st.success(f"已{'启用' if new_status else '禁用'} {platform['platform_name']}")
                            st.rerun()

    with platform_tabs[1]:
        st.subheader("📤 分发任务管理")

        # 创建新任务
        with st.expander("➕ 创建分发任务", expanded=True):
            task_name = st.text_input("任务名称", placeholder="例如：3 月新品批量上架")

            selected_platforms = st.multiselect(
                "选择目标平台",
                [p['platform_name'] for p in enabled_platforms],
                default=[p['platform_name'] for p in enabled_platforms if p['platform_type'] == 'domestic_wholesale']
            )

            # 产品选择
            product_options = {p['型号']: p['id'] for p in st.session_state.products}
            selected_products = st.multiselect(
                "选择产品",
                list(product_options.keys()),
                help="可选择多个产品批量分发到各平台"
            )

            if st.button("🚀 创建分发任务"):
                if task_name and selected_platforms and selected_products:
                    product_ids = [product_options[name] for name in selected_products]
                    task_id = PlatformManager.create_distribution_task(
                        task_name=task_name,
                        task_type="batch_upload",
                        platform_list=selected_platforms,
                        product_ids=product_ids
                    )
                    st.success(f"✅ 任务已创建！任务 ID: {task_id}")
                else:
                    st.warning("请填写完整信息")

        st.divider()

        # 任务列表
        st.markdown("#### 📋 任务列表")
        tasks = PlatformManager.get_distribution_tasks()

        if tasks:
            for task in tasks:
                status_icons = {
                    'pending': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }

                with st.expander(f"{status_icons.get(task['status'], '📋')} {task['task_name']} - {task['created_at']}"):
                    st.markdown(f"**目标平台：** {task['platform_list']}")
                    st.markdown(f"**产品数量：** {len(task['product_ids'].split(','))} 个")
                    st.markdown(f"**状态：** {task['status']}")
                    if task['success_count'] or task['failed_count']:
                        st.markdown(f"**结果：** 成功 {task['success_count']} / 失败 {task['failed_count']}")

        else:
            st.info("暂无分发任务")

    with platform_tabs[2]:
        st.subheader("📦 订单管理")
        st.info(" 订单数据需对接各平台 API 自动同步")

        # 订单筛选
        order_platforms = st.multiselect(
            "选择平台",
            [p['platform_name'] for p in platforms],
            key="order_platform_filter"
        )

        st.markdown("**最近订单**")
        st.table(pd.DataFrame(columns=['订单号', '平台', '产品', '金额', '状态', '时间']))

    with platform_tabs[3]:
        st.subheader("📊 数据统计")

        stats = PlatformManager.get_platform_statistics()

        if stats['platform_stats']:
            st.markdown("#### 各平台产品分布")
            platform_df = pd.DataFrame(stats['platform_stats'])
            st.bar_chart(platform_df.set_index('platform_name')['total'])

            st.markdown("#### 各平台销售统计")
            if stats['order_stats']:
                order_df = pd.DataFrame(stats['order_stats'])
                st.bar_chart(order_df.set_index('platform_name')['total_amount'])
        else:
            st.info("暂无统计数据")

    st.divider()
    st.markdown("""
    **💡 提示：**
    - 各平台 API 配置需在 `.env` 文件中设置对应的 `api_key` 和 `api_secret`
    - 启用自动定价后，系统会根据预设策略自动调整各平台价格
    - 订单数据每 30 分钟自动同步一次
    """)

# ==================== 页面 6: 销售数据 ====================
elif menu == "💰 销售数据":
    st.header("💰 销售数据实时看板")

    # 数据源选择
    data_source = st.segmented_control(
        "数据源",
        ["1688", "淘宝", "京东", "拼多多", "全部"]
    )

    st.divider()

    # 核心指标
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("今日销售额", "¥0.00", "数据待同步")
    col2.metric("今日订单", "0", "数据待同步")
    col3.metric("转化率", "0%", "数据待同步")
    col4.metric("客单价", "¥0.00", "数据待同步")

    st.divider()

    # 销售趋势图
    st.subheader("📈 销售趋势")

    dates = pd.date_range(start='2026-03-01', periods=22)
    sample_sales = pd.DataFrame({
        '日期': dates,
        '销售额': [i * 150 + (i % 7) * 50 for i in range(22)],
        '订单数': [i * 2 + (i % 5) for i in range(22)]
    })

    fig = px.line(sample_sales, x='日期', y='销售额',
                 title='3 月销售趋势（示例数据）',
                 markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.info("🔌 数据源连接状态：未连接 - 需配置 1688 API")

# ==================== 页面 5: 团队任务 ====================
elif menu == "👥 团队任务":
    st.header("👥 团队任务管理")

    # 团队成员
    st.subheader("👤 团队成员")

    team_cols = st.columns(4)

    team_members = [
        {"name": "KR (任光成)", "role": "GM/管理者", "location": "中山", "status": "在线"},
        {"name": "工程师 A", "role": "软件工程师", "location": "中山", "status": "在线"},
        {"name": "工程师 B", "role": "硬件工程师", "location": "中山", "status": "离线"},
        {"name": "业务 A", "role": "业务 + 美工", "location": "中山", "status": "在线"}
    ]

    for i, member in enumerate(team_members):
        with team_cols[i % 4]:
            st.markdown(f"""
            <div style="background: #f3f4f6; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                <div style="font-size: 2rem;">{'👨‍💼' if 'GM' in member['role'] else '👨‍💻' if '软件' in member['role'] else '🔧' if '硬件' in member['role'] else '🎨'}</div>
                <div style="font-weight: bold;">{member['name']}</div>
                <div style="font-size: 0.875rem; color: #6b7280;">{member['role']}</div>
                <div style="font-size: 0.75rem; color: #9ca3af;">{member['location']}</div>
                <span class="status-badge {'status-success' if member['status'] == '在线' else 'status-danger'}">
                    {member['status']}
                </span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # 任务看板
    st.subheader("📋 任务看板")

    task_col1, task_col2 = st.columns(2)

    with task_col1:
        st.markdown("#### 📝 待办任务")
        st.warning("""
        - [ ] PDF 解析工具测试
        - [ ] 1688 API 对接
        - [ ] 产品数据录入
        """)

    with task_col2:
        st.markdown("#### ✅ 已完成")
        st.success("""
        - [x] Streamlit 看板搭建
        - [x] Python 环境配置
        - [x] 项目初始化
        """)

    # 新建任务
    st.divider()
    st.subheader("➕ 新建任务")

    new_task_col1, new_task_col2, new_task_col3 = st.columns(3)

    with new_task_col1:
        task_assignee = st.selectbox("负责人", [m['name'] for m in team_members])

    with new_task_col2:
        task_content = st.text_input("任务内容")

    with new_task_col3:
        if st.button("添加任务", type="primary"):
            st.session_state.tasks.append({
                'assignee': task_assignee,
                'content': task_content,
                'status': '待办',
                'created_at': datetime.now().isoformat()
            })
            st.success("任务已添加！")

# ==================== 页面 6: 公众号发布 ====================
elif menu == "📱 公众号发布":
    st.header("📱 微信公众号自动发布")

    st.markdown("""
    ### 🎯 功能说明

    从 PDF 解析到公众号发布的全自动工作流：

    ```
    PDF 规格书 → 数据提取 → 文案生成 → 公众号发布
    ```

    ---
    """)

    # 步骤 1: 选择产品
    st.subheader("1️⃣ 选择产品")

    if not st.session_state.products:
        st.warning("暂无产品数据，请先上传 PDF 规格书")
    else:
        # 产品选择器
        product_options = {
            f"{p.get('型号', 'N/A')} - {p.get('名称', 'N/A')}" : p
            for p in st.session_state.products
        }
        selected_product_str = st.selectbox(
            "选择要发布的产品",
            list(product_options.keys())
        )
        selected_product = product_options[selected_product_str]

        # 显示产品信息
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"""
            **型号**: {selected_product.get('型号', 'N/A')}
            **名称**: {selected_product.get('名称', 'N/A')}
            **封装**: {selected_product.get('封装', 'N/A')}
            **应用**: {', '.join(selected_product.get('applications', ['待确认']))}
            """)

        with col2:
            st.success(f"""
            **关键参数**:
            - 效率：{selected_product.get('efficiency', '待测试')}
            - 纹波：{selected_product.get('ripple', '待测试')}
            - 温升：{selected_product.get('temp_rise', '待测试')}
            """)

        st.divider()

        # 步骤 2: 生成文案
        st.subheader("2️⃣ 生成文案")

        content_type = st.radio(
            "选择内容类型",
            ["公众号推文", "知乎技术文", "朋友圈文案", "视频脚本", "1688 详情页"],
            horizontal=True
        )

        if st.button("🪄 一键生成文案", type="primary"):
            with st.spinner("正在生成文案..."):
                # 强制重新加载模块，确保使用最新代码
                if 'content_generator' in sys.modules:
                    importlib.reload(sys.modules['content_generator'])

                # 调用内容生成器
                from content_generator import ContentGenerator

                # 准备测试数据
                test_data = {
                    'chip_type': selected_product.get('chip_type', 'DC-DC 芯片'),
                    'efficiency': selected_product.get('efficiency', '91%'),
                    'temp_rise': selected_product.get('temp_rise', '35°C'),
                    'ripple': selected_product.get('ripple', '80mV'),
                }

                # 创建生成器
                generator = ContentGenerator(
                    model=selected_product.get('型号', 'N/A'),
                    test_data=test_data
                )

                # 根据选择生成内容
                if content_type == "公众号推文":
                    content = generator.generate_wechat_article()
                elif content_type == "知乎技术文":
                    content = generator.generate_zhihu_article()
                elif content_type == "朋友圈文案":
                    moments = generator.generate_wechat_moments()
                    content = "\n\n---\n\n".join(moments)
                elif content_type == "视频脚本":
                    content = generator.generate_video_script()
                else:  # 1688 详情页
                    # 导出 1688 详情页
                    output_dir = Path("output/1688")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    model = selected_product.get('型号', 'N/A')

                    # 生成 HTML 和 Markdown
                    html_path = output_dir / f"{model}_1688 详情页_{timestamp}.html"
                    md_path = output_dir / f"{model}_1688 详情页_{timestamp}.md"

                    # 使用内嵌生成器
                    generator_1688 = ProductDetailGenerator(selected_product)
                    html_content = generator_1688.generate_html()
                    md_content = generator_1688.generate_markdown()

                    # 保存文件
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(md_content)

                    # 保存记录到数据库
                    product_id = selected_product.get('id')
                    if product_id:
                        DetailPageManager.add_record(product_id, model, str(html_path), str(md_path))

                    content = f"""✅ **1688 详情页已生成!**

📁 **导出文件**:
- HTML: `{html_path}`
- Markdown: `{md_path}`

📌 **使用说明**:
1. HTML 文件可直接在浏览器中打开预览
2. 将 HTML 内容复制到 1688 卖家后台
3. 或使用 Markdown 文件导入到支持 MD 的编辑器

🔗 **直接打开**:
- [🌐 在浏览器中打开 HTML 文件](file://{html_path.absolute().as_posix()})
- [📄 查看 Markdown 文件](file://{md_path.absolute().as_posix()})
"""

                # 保存到 session
                st.session_state.generated_content = content

                st.success("✅ 文案生成成功！")

        # 显示生成的文案
        if 'generated_content' in st.session_state:
            st.divider()
            st.subheader("3️⃣ 预览文案")

            st.markdown(st.session_state.generated_content)

            # 导出按钮
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📥 导出为 Markdown", use_container_width=True):
                    from pathlib import Path
                    output_dir = Path("output/wechat")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_file = output_dir / f"{selected_product.get('型号', 'N/A')}_{content_type}_{timestamp}.md"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(st.session_state.generated_content)
                    st.success(f"已导出：{output_file}")

            with col2:
                if st.button("📋 复制到剪贴板", use_container_width=True):
                    st.code(st.session_state.generated_content)
                    st.info("请手动复制上方代码框中的内容")

            with col3:
                if st.button("🚀 发布到公众号", use_container_width=True):
                    st.info("""
                    ### 📱 启动发布助手

                    1. 点击下方"启动发布助手"按钮
                    2. 浏览器会自动打开公众号后台
                    3. 扫码登录公众号
                    4. 自动填充标题和内容
                    5. **人工审核后点击发布**

                    **注意**: 发布前请务必检查内容准确性！
                    """)

                    if st.button("🌐 启动发布助手"):
                        import subprocess
                        try:
                            # 启动发布脚本
                            subprocess.Popen(
                                ['python', 'scripts\\wechat_publisher.py', '--demo'],
                                cwd=project_root,
                                creationflags=subprocess.CREATE_NEW_CONSOLE
                            )
                            st.success("🚀 发布助手已启动！")
                        except Exception as e:
                            st.error(f"启动失败：{e}")

        st.divider()

        # 使用说明
        st.info("""
        ### 💡 使用流程

        1. **选择产品**: 从下拉列表选择要推广的产品
        2. **生成文案**: 点击"一键生成文案"，AI 自动撰写
        3. **预览编辑**: 检查文案内容，可手动调整
        4. **导出/复制**: 导出为文件或复制到剪贴板
        5. **发布到公众号**: 启动自动发布助手，人工审核后发布

        ---

        **支持的内容类型**:
        - **公众号推文**: 适合微信公众号，图文结合
        - **知乎技术文**: 技术向长文，建立专业度
        - **朋友圈文案**: 短小精悍，适合朋友圈传播
        - **视频脚本**: 30 秒产品视频分镜头脚本
        - **1688 详情页**: 电商平台产品详情页 HTML

        """)

# ==================== 页面 7: 自动化流程 ====================
elif menu == "⚙️ 自动化流程":
    st.header("⚙️ 自动化流程追踪")

    st.markdown("""
    ### 🔄 芯片产品全生命周期流程

    ```
    PDF 规格书上传 → 自动解析 → 产品库 → 1688 上架 → 销售监控 → 数据同步
                                              ↓
                                         公众号发布
    ```

    ---
    """)

    # 流程图
    st.subheader("📊 当前流程状态")

    flow_steps = [
        ("📄 PDF 上传", "completed" if st.session_state.products else "pending"),
        ("🔍 智能解析", "completed" if st.session_state.products else "pending"),
        ("📦 产品入库", "completed" if st.session_state.products else "pending"),
        ("🛒 1688 上架", "pending"),
        ("💰 销售监控", "pending"),
        ("📱 公众号发布", "pending"),
    ]

    for i, (step, status) in enumerate(flow_steps):
        col = st.columns(6)[i % 6]
        with col:
            if status == "completed":
                st.success(f"**{step}**\n\n✅")
            else:
                st.info(f"**{step}**\n\n⏳")

    st.divider()

    # 新增：公众号发布流程
    st.subheader("📱 公众号发布工作流")

    pub_col1, pub_col2, pub_col3 = st.columns(3)

    with pub_col1:
        st.markdown("""
        #### 📝 内容生成
        - AI 自动撰写文案
        - 支持多平台适配
        - 一键导出/复制
        """)

    with pub_col2:
        st.markdown("""
        #### 🤖 自动发布
        - RPA 浏览器自动化
        - 自动填充内容
        - 自动上传图片
        """)

    with pub_col3:
        st.markdown("""
        #### ✅ 人工审核
        - 内容准确性检查
        - 排版调整
        - 最终发布确认
        """)

    st.divider()

    # 多平台电商自动化
    st.subheader("🌐 多平台电商自动化")

    platform_tabs = st.tabs(["1688", "淘宝/天猫", "京东", "拼多多", "抖音电商", "小红书", "闲鱼", "亚马逊", "独立站"])

    with platform_tabs[0]:  # 1688
        st.markdown("""
        ####  1688 平台自动化
        **已实现功能：**
        - ✅ 产品批量上架
        - ✅ 价格自动调整
        - ✅ 库存同步
        - ✅ 订单处理
        - ✅ 销售数据统计

        **自动化流程：**
        `产品入库` → `文案生成` → `主图优化` → `批量上架` → `状态监控` → `数据同步`
        """)
        st.toggle("启用 1688 自动化", value=True, key="auto_1688")

    with platform_tabs[1]:  # 淘宝/天猫
        st.markdown("""
        #### 🔵 淘宝/天猫平台自动化
        **已实现功能：**
        - ⏳ 产品一键分发
        - ⏳ 直通车广告投放
        - ⏳ 淘宝客推广
        - ⏳ 活动报名
        - ⏳ 评价管理

        **自动化流程：**
        `产品同步` → `详情页适配` → `价格策略` → `自动上架` → `推广投放` → `数据监控`
        """)
        st.toggle("启用淘宝自动化", value=False, key="auto_taobao")

    with platform_tabs[2]:  # 京东
        st.markdown("""
        #### 🔴 京东平台自动化
        **已实现功能：**
        - ⏳ 产品上架
        - ⏳ 京东快车投放
        - ⏳ 京挑客推广
        - ⏳ 仓储物流对接
        - ⏳ 售后服务

        **自动化流程：**
        `产品同步` → `京东适配` → `入仓管理` → `自动上架` → `配送跟踪` → `售后处理`
        """)
        st.toggle("启用京东自动化", value=False, key="auto_jd")

    with platform_tabs[3]:  # 拼多多
        st.markdown("""
        #### 🟠 拼多多平台自动化
        **已实现功能：**
        - ⏳ 批量上架
        - ⏳ 拼单管理
        - ⏳ 百亿补贴报名
        - ⏳ 推广计划
        - ⏳ 客服自动回复

        **自动化流程：**
        `选品同步` → `低价策略` → `活动报名` → `自动上架` → `拼单处理` → `客服响应`
        """)
        st.toggle("启用拼多多自动化", value=False, key="auto_pdd")

    with platform_tabs[4]:  # 抖音电商
        st.markdown("""
        #### ⚫ 抖音电商自动化
        **已实现功能：**
        - ⏳ 抖音小店上架
        - ⏳ 短视频带货
        - ⏳ 直播带货数据
        - ⏳ 巨量千川投放
        - ⏳ 达人合作对接

        **自动化流程：**
        `商品同步` → `视频素材` → `直播排期` → `广告投放` → `带货分佣` → `订单履约`
        """)
        st.toggle("启用抖音电商自动化", value=False, key="auto_douyin")

    with platform_tabs[5]:  # 小红书
        st.markdown("""
        #### 🟢 小红书平台自动化
        **已实现功能：**
        - ⏳ 笔记种草
        - ⏳ 商品卡片
        - ⏳ KOL/KOC合作
        - ⏳ 品牌号运营
        - ⏳ 私域引流

        **自动化流程：**
        `产品选品` → `笔记创作` → `达人对接` → `投放种草` → `引流转化` → `数据追踪`
        """)
        st.toggle("启用小红书自动化", value=False, key="auto_xiaohongshu")

    with platform_tabs[6]:  # 闲鱼
        st.markdown("""
        #### 🟡 闲鱼平台自动化
        **已实现功能：**
        - ⏳ 批量发布
        - ⏳ 自动擦亮
        - ⏳ 智能定价
        - ⏳ 自动回复
        - ⏳ 订单处理

        **自动化流程：**
        `选品导入` → `文案生成` → `多账号发布` → `自动擦亮` → `客户咨询` → `成交发货`
        """)
        st.toggle("启用闲鱼自动化", value=False, key="auto_xianyu")

    with platform_tabs[7]:  # 亚马逊
        st.markdown("""
        #### 🟠 亚马逊 (Amazon) 自动化
        **已实现功能：**
        - ⏳ FBA 发货
        - ⏳ 广告 PPC 管理
        - ⏳ 评论管理
        - ⏳ 库存预警
        - ⏳ 跟卖监控

        **自动化流程：**
        `产品上传` → `FBA 入仓` → `Listing 优化` → `广告投放` → `评论监控` → `库存补货`
        """)
        st.toggle("启用亚马逊自动化", value=False, key="auto_amazon")

    with platform_tabs[8]:  # 独立站
        st.markdown("""
        #### 🌐 独立站 (Shopify/WordPress) 自动化
        **已实现功能：**
        - ⏳ 商品自动同步
        - ⏳ SEO 优化
        - ⏳ 邮件营销
        - ⏳ Facebook/Google 广告
        - ⏳ 订单处理

        **自动化流程：**
        `产品同步` → `SEO 优化` → `广告投放` → `订单处理` → `邮件营销` → `数据分析`
        """)
        st.toggle("启用独立站自动化", value=False, key="auto_independent")

    st.divider()

    # 自动化配置
    st.subheader("🔧 自动化配置")

    auto_col1, auto_col2, auto_col3 = st.columns(3)

    with auto_col1:
        st.markdown("#### 已启用的自动化")
        st.toggle("PDF 自动解析", value=True)
        st.toggle("文案自动生成", value=True)
        st.toggle("多平台分发", value=False)

    with auto_col2:
        st.markdown("#### 监控与同步")
        st.toggle("上架状态监控", value=False)
        st.toggle("销售数据同步", value=False)
        st.toggle("库存预警", value=False)

    with auto_col3:
        st.markdown("#### 定时任务")
        st.time_input("每日数据同步", value=time(9, 0))
        st.time_input("库存检查", value=time(12, 0))
        st.time_input("价格调整", value=time(18, 0))

# ==================== 页脚 ====================
st.divider()
st.markdown(
    "<div style='text-align: center; color: #9ca3af; padding: 1rem;'>"
    "🎯 芯片产品作战看板 | Powered by Streamlit + Claude Code | "
    f"最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>",
    unsafe_allow_html=True
)
