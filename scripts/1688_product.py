#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 产品详情页生成器

功能:
- 基于产品库数据自动生成 1688 产品详情页
- 支持 HTML 和 Markdown 两种格式导出
- 包含产品主图、详情图、参数表、应用场景等模块
- 适配 1688 平台SEO优化

作者：KR
日期：2026-03-22
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class ProductDetailGenerator:
    """1688 产品详情页生成器"""

    def __init__(self, product_data: Dict[str, Any]):
        """
        初始化生成器

        Args:
            product_data: 产品数据字典，包含型号、参数等信息
        """
        self.product = product_data
        self.model = product_data.get('型号', 'N/A')
        self.name = product_data.get('品名', '芯片产品')
        self.brand = product_data.get('品牌', '冠辰科技')
        self.category = product_data.get('分类', 'LED 驱动芯片')

    def generate_html(self) -> str:
        """
        生成 HTML 格式详情页

        Returns:
            完整的 HTML 详情页内容
        """
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.name} - {self.model} | 1688 产品详情页</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #ff6a00, #ff9900); color: white; padding: 40px 20px; text-align: center; }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header .model {{ font-size: 24px; opacity: 0.9; }}
        .section {{ background: white; margin: 20px 0; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .section-title {{ font-size: 24px; color: #ff6a00; border-left: 4px solid #ff6a00; padding-left: 15px; margin-bottom: 20px; }}
        .param-table {{ width: 100%; border-collapse: collapse; }}
        .param-table th, .param-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        .param-table th {{ background: #f9f9f9; font-weight: 600; width: 30%; }}
        .param-table tr:hover {{ background: #fafafa; }}
        .highlight {{ color: #ff6a00; font-weight: 600; }}
        .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }}
        .feature-card {{ background: linear-gradient(135deg, #fff5eb, #ffffff); padding: 20px; border-radius: 8px; border-left: 3px solid #ff6a00; }}
        .feature-card h3 {{ color: #333; margin-bottom: 10px; }}
        .feature-card p {{ color: #666; line-height: 1.6; }}
        .images {{ text-align: center; margin: 20px 0; }}
        .images img {{ max-width: 100%; height: auto; border-radius: 8px; }}
        .application {{ background: #f9f9f9; padding: 20px; border-radius: 8px; margin-top: 20px; }}
        .application ul {{ list-style: none; }}
        .application li {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
        .application li:before {{ content: "✓"; color: #ff6a00; font-weight: bold; margin-right: 10px; }}
        .footer {{ text-align: center; padding: 30px; color: #999; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.name}</h1>
        <div class="model">型号：{self.model}</div>
        <div style="margin-top: 15px; font-size: 18px;">{self.brand} | {self.category}</div>
    </div>

    <div class="container">
        <!-- 产品亮点 -->
        <div class="section">
            <h2 class="section-title">✨ 产品亮点</h2>
            <div class="features">
                {self._generate_feature_cards()}
            </div>
        </div>

        <!-- 产品图片 -->
        <div class="section">
            <h2 class="section-title">📷 产品实拍</h2>
            <div class="images">
                <div style="background: #f0f0f0; height: 400px; display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                    <span style="color: #999; font-size: 18px;">产品主图区域 (请替换为实际产品图片)</span>
                </div>
            </div>
        </div>

        <!-- 技术参数 -->
        <div class="section">
            <h2 class="section-title">⚙️ 技术参数</h2>
            <table class="param-table">
                {self._generate_param_rows()}
            </table>
        </div>

        <!-- 应用领域 -->
        <div class="section">
            <h2 class="section-title">🎯 应用领域</h2>
            <div class="application">
                {self._generate_applications()}
            </div>
        </div>

        <!-- 包装信息 -->
        <div class="section">
            <h2 class="section-title">📦 包装信息</h2>
            <table class="param-table">
                <tr><th>包装方式</th><td>卷带包装 (Tape & Reel)</td></tr>
                <tr><th>最小起订量</th><td>100  pcs</td></tr>
                <tr><th>供货能力</th><td>100,000 pcs/周</td></tr>
                <tr><th>交货周期</th><td>现货 / 3-5 天</td></tr>
            </table>
        </div>

        <!-- 公司介绍 -->
        <div class="section">
            <h2 class="section-title">🏢 关于我们</h2>
            <div style="line-height: 1.8; color: #666;">
                <p><strong>中山市冠辰科技</strong> 专注于 LED 驱动芯片和智能照明解决方案的研发与销售。</p>
                <p style="margin-top: 15px;">📍 地址：广东省中山市古镇镇</p>
                <p>📞 电话：请咨询客服</p>
                <p>📧 邮箱：请联系获取</p>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>© 2026 冠辰科技 版权所有</p>
        <p>本页面内容仅供参考，具体参数以实际产品为准</p>
    </div>
</body>
</html>"""
        return html

    def generate_markdown(self) -> str:
        """
        生成 Markdown 格式详情页

        Returns:
            Markdown 格式的详情页内容
        """
        md = f"""# {self.name} - {self.model}

**品牌**: {self.brand} | **分类**: {self.category}

---

## ✨ 产品亮点

{self._generate_markdown_features()}

---

## 📷 产品实拍

![产品主图](请替换为实际产品图片 URL)

*产品实拍图 - {self.name}*

---

## ⚙️ 技术参数

{self._generate_markdown_params()}

---

## 🎯 应用领域

{self._generate_markdown_applications()}

---

## 📦 包装信息

| 项目 | 规格 |
|------|------|
| 包装方式 | 卷带包装 (Tape & Reel) |
| 最小起订量 | 100 pcs |
| 供货能力 | 100,000 pcs/周 |
| 交货周期 | 现货 / 3-5 天 |

---

## 🏢 关于我们

**中山市冠辰科技** 专注于 LED 驱动芯片和智能照明解决方案的研发与销售。

- 📍 地址：广东省中山市古镇镇
- 📞 电话：请咨询客服
- 📧 邮箱：请联系获取

---

© 2026 冠辰科技 版权所有
"""
        return md

    def _generate_feature_cards(self) -> str:
        """生成产品亮点卡片 HTML"""
        features = []

        # 从产品数据中提取亮点
        efficiency = self.product.get('效率', '')
        if efficiency:
            features.append(f"""
                <div class="feature-card">
                    <h3>⚡ 高效率</h3>
                    <p>转换效率高达 <span class="highlight">{efficiency}</span>, 降低能耗，提升系统性能</p>
                </div>
            """)

        frequency = self.product.get('开关频率', '')
        if frequency:
            features.append(f"""
                <div class="feature-card">
                    <h3>📡 高频工作</h3>
                    <p>开关频率 <span class="highlight">{frequency}</span>, 支持小型化设计</p>
                </div>
            """)

        accuracy = self.product.get('电流精度', '')
        if accuracy:
            features.append(f"""
                <div class="feature-card">
                    <h3>🎯 高精度</h3>
                    <p>电流精度 <span class="highlight">{accuracy}</span>, 输出稳定一致</p>
                </div>
            """)

        protection = self.product.get('保护功能', '过流保护/过温保护')
        features.append(f"""
            <div class="feature-card">
                <h3>🛡️ 完善保护</h3>
                <p>{protection}, 确保系统安全可靠</p>
            </div>
        """)

        features.append(f"""
            <div class="feature-card">
                <h3>🔧 易用设计</h3>
                <p>外围电路简单，支持快速开发，缩短产品上市周期</p>
            </div>
        """)

        return '\n'.join(features)

    def _generate_param_rows(self) -> str:
        """生成参数表格 HTML 行"""
        params = [
            ('产品型号', self.model),
            ('产品名称', self.name),
            ('品牌', self.brand),
            ('分类', self.category),
            ('输入电压', self.product.get('输入电压', 'N/A')),
            ('输出电压', self.product.get('输出电压', 'N/A')),
            ('输出电流', self.product.get('输出电流', 'N/A')),
            ('效率', self.product.get('效率', 'N/A')),
            ('开关频率', self.product.get('开关频率', 'N/A')),
            ('电流精度', self.product.get('电流精度', 'N/A')),
            ('工作温度', self.product.get('工作温度', 'N/A')),
            ('封装形式', self.product.get('封装形式', 'N/A')),
            ('保护功能', self.product.get('保护功能', 'N/A')),
        ]

        rows = []
        for name, value in params:
            if value and value != 'N/A':
                rows.append(f"<tr><th>{name}</th><td>{value}</td></tr>")
        return '\n'.join(rows)

    def _generate_applications(self) -> str:
        """生成应用领域 HTML"""
        apps = []

        category = self.category.lower()
        if 'LED' in category or '照明' in category:
            apps = [
                '室内照明：筒灯、射灯、面板灯、吸顶灯',
                '商业照明：轨道灯、格栅灯、吊灯',
                '装饰照明：灯带、线条灯、点光源',
                '智能照明：可调光调色驱动系统',
                '工业照明：工矿灯、投光灯、路灯',
            ]
        else:
            apps = [
                '消费电子：智能家居、小家电',
                '工业控制：自动化设备、仪器仪表',
                '汽车电子：车载照明、车载电器',
                '医疗设备：医疗仪器、健康监测',
            ]

        return '<ul>' + '\n'.join(f'<li>{app}</li>' for app in apps) + '</ul>'

    def _generate_markdown_features(self) -> str:
        """生成 Markdown 格式产品亮点"""
        features = []

        efficiency = self.product.get('效率', '')
        if efficiency:
            features.append(f"- **⚡ 高效率**: 转换效率高达 {efficiency}, 降低能耗")

        frequency = self.product.get('开关频率', '')
        if frequency:
            features.append(f"- **📡 高频工作**: 开关频率 {frequency}, 支持小型化设计")

        accuracy = self.product.get('电流精度', '')
        if accuracy:
            features.append(f"- **🎯 高精度**: 电流精度 {accuracy}, 输出稳定")

        features.append(f"- **🛡️ 完善保护**: 多重保护功能，确保系统安全")
        features.append(f"- **🔧 易用设计**: 外围电路简单，支持快速开发")

        return '\n'.join(features)

    def _generate_markdown_params(self) -> str:
        """生成 Markdown 格式参数表"""
        params = [
            ('产品型号', self.model),
            ('产品名称', self.name),
            ('品牌', self.brand),
            ('输入电压', self.product.get('输入电压', 'N/A')),
            ('输出电压', self.product.get('输出电压', 'N/A')),
            ('输出电流', self.product.get('输出电流', 'N/A')),
            ('效率', self.product.get('效率', 'N/A')),
            ('开关频率', self.product.get('开关频率', 'N/A')),
            ('电流精度', self.product.get('电流精度', 'N/A')),
            ('工作温度', self.product.get('工作温度', 'N/A')),
            ('封装形式', self.product.get('封装形式', 'N/A')),
        ]

        md = "| 参数名称 | 规格值 |\n|----------|--------|\n"
        for name, value in params:
            if value and value != 'N/A':
                md += f"| {name} | {value} |\n"
        return md

    def _generate_markdown_applications(self) -> str:
        """生成 Markdown 格式应用领域"""
        category = self.category.lower()
        if 'LED' in category or '照明' in category:
            return """- 室内照明：筒灯、射灯、面板灯、吸顶灯
- 商业照明：轨道灯、格栅灯、吊灯
- 装饰照明：灯带、线条灯、点光源
- 智能照明：可调光调色驱动系统
- 工业照明：工矿灯、投光灯、路灯"""
        else:
            return """- 消费电子：智能家居、小家电
- 工业控制：自动化设备、仪器仪表
- 汽车电子：车载照明、车载电器
- 医疗设备：医疗仪器、健康监测"""


def export_1688_detail(product_data: Dict[str, Any], output_dir: str = None) -> tuple:
    """
    导出 1688 产品详情页

    Args:
        product_data: 产品数据字典
        output_dir: 输出目录，默认使用 output/1688

    Returns:
        (html_path, md_path) 元组，返回两个文件的路径
    """
    if output_dir is None:
        output_dir = Path("output/1688")
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    generator = ProductDetailGenerator(product_data)
    model = product_data.get('型号', 'N/A')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 导出 HTML
    html_path = output_dir / f"{model}_1688 详情页_{timestamp}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(generator.generate_html())

    # 导出 Markdown
    md_path = output_dir / f"{model}_1688 详情页_{timestamp}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(generator.generate_markdown())

    return str(html_path), str(md_path)


# 命令行调用入口
if __name__ == "__main__":
    # 测试数据
    test_product = {
        '型号': 'SM8923SBT',
        '品名': '非隔离降压型 LED 恒流驱动芯片',
        '品牌': '冠辰科技',
        '分类': 'LED 驱动芯片',
        '输入电压': '85-265VAC',
        '输出电压': '12-24VDC',
        '输出电流': '350mA',
        '效率': '≥88%',
        '开关频率': '65kHz',
        '电流精度': '±3%',
        '工作温度': '-40℃ ~ +85℃',
        '封装形式': 'SOP-8',
        '保护功能': '过流保护/过温保护/短路保护',
    }

    html_path, md_path = export_1688_detail(test_product)
    print(f"✅ HTML 详情页已导出：{html_path}")
    print(f"✅ Markdown 详情页已导出：{md_path}")
