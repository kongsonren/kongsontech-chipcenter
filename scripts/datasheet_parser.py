"""
芯片规格书自动解析器 (Datasheet Parser)
功能：
1. PDF 文本提取
2. 关键参数自动识别
3. 应用场景 AI 推荐
4. 测试项目自动生成
5. 输出产品分析文档

使用方法:
    python datasheet_parser.py input.pdf --output output_folder
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

# PDF 解析库
try:
    import pdfplumber
except ImportError:
    print("请安装 pdfplumber: pip install pdfplumber")
    exit(1)

# 数据处理
try:
    import pandas as pd
except ImportError:
    print("请安装 pandas: pip install pandas")
    exit(1)


class DatasheetParser:
    """芯片规格书解析器"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = ""
        self.tables = []
        self.product_info = {}
        self.test_items = []

        # 参数提取正则表达式
        self.param_patterns = {
            'input_voltage': [
                r'输入电压[:：]?\s*([\d\.]+)\s*[-~]\s*([\d\.]+)\s*V',
                r'Input Voltage\s*[:：]?\s*([\d\.]+)\s*[-~]\s*([\d\.]+)\s*V',
                r'VIN\s*[:：]?\s*([\d\.]+)\s*[-~]\s*([\d\.]+)\s*V',
            ],
            'output_voltage': [
                r'输出电压[:：]?\s*([\d\.]+)\s*[-~]\s*([\d\.]+)\s*V',
                r'Output Voltage\s*[:：]?\s*([\d\.]+)\s*[-~]\s*([\d\.]+)\s*V',
                r'VOUT\s*[:：]?\s*([\d\.]+)\s*[-~]\s*([\d\.]+)\s*V',
            ],
            'output_current': [
                r'输出电流[:：]?\s*([\d\.]+)\s*A',
                r'Output Current\s*[:：]?\s*([\d\.]+)\s*A',
                r'IOUT\s*[:：]?\s*([\d\.]+)\s*A',
            ],
            'switching_freq': [
                r'开关频率[:：]?\s*([\d\.]+)\s*(kHz|MHz)',
                r'Switching Frequency\s*[:：]?\s*([\d\.]+)\s*(kHz|MHz)',
                r'fSW\s*[:：]?\s*([\d\.]+)\s*(kHz|MHz)',
            ],
            'efficiency': [
                r'效率[:：]?\s*([\d\.]+)\s*%',
                r'Efficiency\s*[:：]?\s*([\d\.]+)\s*%',
                r'η\s*[:：]?\s*([\d\.]+)\s*%',
            ],
            'package': [
                r'封装[:：]?\s*(\w+\s*[-]?\s*\d+)',
                r'Package\s*[:：]?\s*(\w+\s*[-]?\s*\d+)',
                r'(TO-\d+|SOP-\d+|QFN-\d+|TSSOP-\d+)',
            ],
            'operating_temp': [
                r'工作温度[:：]?\s*(-?\d+)\s*[-~+]\s*(\d+)\s*°?C',
                r'Operating Temperature\s*[:：]?\s*(-?\d+)\s*[-~+]\s*(\d+)\s*°?C',
            ],
        }

        # 芯片类型关键词
        self.chip_types = {
            'DC-DC 降压': ['Buck', '降压', 'Step-Down', 'Step Down'],
            'DC-DC 升压': ['Boost', '升压', 'Step-Up', 'Step Up'],
            'LDO': ['LDO', '低压差', 'Low Dropout'],
            'LED 驱动': ['LED Driver', 'LED 驱动', '背光驱动'],
            'MOSFET': ['MOSFET', '场效应管', '功率管'],
            '运放': ['Op Amp', '运算放大器', 'Operational Amplifier'],
            'MCU': ['MCU', '微控制器', 'Microcontroller'],
        }

    def extract_text(self) -> str:
        """从 PDF 提取文本"""
        print(f"正在解析 PDF: {self.pdf_path}")

        with pdfplumber.open(self.pdf_path) as pdf:
            # 提取所有文本
            self.text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    self.text += text + "\n"

            # 提取表格
            self.tables = []
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    self.tables.append({
                        'page': i + 1,
                        'data': table
                    })

        print(f"✓ 提取文本成功，共 {len(self.text)} 字符，{len(self.tables)} 个表格")
        return self.text

    def extract_parameters(self) -> dict:
        """提取关键参数"""
        print("正在提取关键参数...")

        for param_name, patterns in self.param_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, self.text, re.IGNORECASE)
                if matches:
                    # 取第一个匹配结果
                    match = matches[0]
                    if isinstance(match, tuple):
                        self.product_info[param_name] = {
                            'min': match[0],
                            'max': match[1] if len(match) > 1 else match[0],
                            'unit': match[-1] if not match[-1].isdigit() else 'V'
                        }
                    else:
                        self.product_info[param_name] = match
                    break

        print(f"✓ 提取 {len(self.product_info)} 个参数")
        return self.product_info

    def identify_chip_type(self) -> str:
        """识别芯片类型"""
        print("正在识别芯片类型...")

        for chip_type, keywords in self.chip_types.items():
            for keyword in keywords:
                if keyword.lower() in self.text.lower():
                    print(f"✓ 识别芯片类型：{chip_type}")
                    return chip_type

        return "未知类型"

    def extract_product_info(self) -> dict:
        """提取完整产品信息"""
        # 从文件名提取型号
        filename = Path(self.pdf_path).stem
        self.product_info['model'] = self._extract_model_from_text(filename)
        self.product_info['chip_type'] = self.identify_chip_type()

        # 提取制造商
        self.product_info['manufacturer'] = self._extract_manufacturer()

        # 提取关键参数
        self.extract_parameters()

        # 提取应用领域
        self.product_info['applications'] = self._extract_applications()

        # 提取主要特性
        self.product_info['features'] = self._extract_features()

        return self.product_info

    def _extract_model_from_text(self, text: str) -> str:
        """从文本提取型号"""
        # 常见型号模式
        patterns = [
            r'([A-Z]{2,}\d{3,}[A-Z]*)',  # 如 LM2596, MP1584
            r'([A-Z]{2,}-\d{3,})',        # 如 TPS-2596
            r'(\d{3,}[A-Z]{2,})',         # 如 2596DC
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]

        return text.upper()

    def _extract_manufacturer(self) -> str:
        """提取制造商"""
        manufacturers = {
            'TI': ['Texas Instruments', '德州仪器', 'TI '],
            'ST': ['STMicroelectronics', '意法半导体', 'ST '],
            'NXP': ['NXP', '恩智浦', 'NXP '],
            'Infineon': ['Infineon', '英飞凌', 'Infineon '],
            'ADI': ['Analog Devices', '亚德诺', 'ADI '],
            'Maxim': ['Maxim', '美信', 'Maxim '],
            'MPS': ['Monolithic Power Systems', 'MPS ', '芯源系统'],
            'ON': ['ON Semiconductor', '安森美', 'ON '],
        }

        for manu, keywords in manufacturers.items():
            for keyword in keywords:
                if keyword.lower() in self.text.lower():
                    return manu

        return "未知厂商"

    def _extract_applications(self) -> list:
        """提取应用领域"""
        applications = []

        app_keywords = {
            'LED 照明': ['LED', '照明', '灯具', '背光'],
            '汽车电子': ['汽车', '车载', '车用', 'Automotive'],
            '工业控制': ['工业', '工控', 'Industrial'],
            '消费电子': ['消费', '手机', '平板', 'Consumer'],
            '通信设备': ['通信', '网络', 'Telecom'],
            '医疗设备': ['医疗', '医用', 'Medical'],
            '电源适配器': ['适配器', '充电器', 'Adapter', 'Charger'],
        }

        for app, keywords in app_keywords.items():
            for keyword in keywords:
                if keyword.lower() in self.text.lower():
                    applications.append(app)
                    break

        return applications if applications else ['通用电源']

    def _extract_features(self) -> list:
        """提取主要特性"""
        features = []

        feature_patterns = [
            (r'效率 [ 为:：]?(\d+)%', '高效率'),
            (r'低功耗', '低功耗'),
            (r'过流保护|OCP', '过流保护'),
            (r'过压保护|OVP', '过压保护'),
            (r'过热保护|OTP', '过热保护'),
            (r'软启动', '软启动'),
            (r'同步整流', '同步整流'),
            (r'可调频率', '频率可调'),
        ]

        for pattern, feature_name in feature_patterns:
            if re.search(pattern, self.text, re.IGNORECASE):
                features.append(feature_name)

        return features

    def generate_test_items(self) -> list:
        """生成测试项目清单"""
        chip_type = self.product_info.get('chip_type', '')

        test_templates = {
            'DC-DC 降压': [
                {'name': '效率测试', 'description': '测量 25%/50%/75%/100% 负载下的效率', 'priority': '高'},
                {'name': '线性调整率', 'description': '输入电压变化时的输出电压稳定性', 'priority': '高'},
                {'name': '负载调整率', 'description': '负载变化时的输出电压稳定性', 'priority': '高'},
                {'name': '纹波噪声', 'description': '输出纹波电压峰峰值', 'priority': '中'},
                {'name': '温升测试', 'description': '满载 1 小时温升', 'priority': '中'},
                {'name': '启动特性', 'description': '上电启动时间与过冲', 'priority': '低'},
            ],
            'LDO': [
                {'name': '压差测试', 'description': '最小压差测量', 'priority': '高'},
                {'name': '线性调整率', 'description': '输入电压变化影响', 'priority': '高'},
                {'name': '负载调整率', 'description': '负载变化影响', 'priority': '高'},
                {'name': 'PSRR', 'description': '电源抑制比', 'priority': '中'},
                {'name': '噪声测试', 'description': '输出噪声电压', 'priority': '中'},
            ],
            'LED 驱动': [
                {'name': '恒流精度', 'description': '输出电流精度测量', 'priority': '高'},
                {'name': '调光功能', 'description': 'PWM/模拟调光测试', 'priority': '高'},
                {'name': '效率测试', 'description': '整灯效率', 'priority': '高'},
                {'name': '保护功能', 'description': '开路/短路保护', 'priority': '中'},
                {'name': '温升测试', 'description': '满载温升', 'priority': '中'},
            ],
        }

        # 根据芯片类型选择测试模板
        self.test_items = test_templates.get(chip_type, test_templates['DC-DC 降压'])

        # 添加通用测试项
        if '过流保护' in self.product_info.get('features', []):
            self.test_items.append({'name': '过流保护测试', 'description': '触发过流保护的电流阈值', 'priority': '中'})
        if '过热保护' in self.product_info.get('features', []):
            self.test_items.append({'name': '过热保护测试', 'description': '触发温度阈值', 'priority': '低'})

        return self.test_items

    def generate_report(self, output_dir: str = 'output') -> str:
        """生成产品分析报告"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model = self.product_info.get('model', 'unknown')

        # 生成 Markdown 报告
        report_md = self._generate_markdown_report()
        md_path = output_path / f"{model}_产品分析_{timestamp}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report_md)
        print(f"✓ 生成 Markdown 报告：{md_path}")

        # 生成 JSON 数据
        json_data = {
            'product_info': self.product_info,
            'test_items': self.test_items,
            'generated_at': timestamp
        }
        json_path = output_path / f"{model}_数据_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"✓ 生成 JSON 数据：{json_path}")

        # 生成测试清单 Excel
        self._generate_test_excel(output_path, timestamp)

        return str(md_path)

    def _generate_markdown_report(self) -> str:
        """生成 Markdown 格式报告"""
        model = self.product_info.get('model', '未知型号')
        chip_type = self.product_info.get('chip_type', '未知类型')
        manufacturer = self.product_info.get('manufacturer', '未知厂商')

        report = f"""# {model} 产品分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**来源文件**: {Path(self.pdf_path).name}

---

## 一、基本信息

| 项目 | 内容 |
|------|------|
| 型号 | {model} |
| 类型 | {chip_type} |
| 制造商 | {manufacturer} |
"""

        # 添加参数表格
        if self.product_info:
            report += "\n## 二、关键参数\n\n"
            report += "| 参数 | 数值 |\n|------|------|\n"

            param_names = {
                'input_voltage': '输入电压',
                'output_voltage': '输出电压',
                'output_current': '输出电流',
                'switching_freq': '开关频率',
                'efficiency': '效率',
                'package': '封装',
                'operating_temp': '工作温度',
            }

            for key, name in param_names.items():
                if key in self.product_info:
                    value = self.product_info[key]
                    if isinstance(value, dict):
                        value_str = f"{value.get('min', '')}-{value.get('max', '')} {value.get('unit', '')}"
                    else:
                        value_str = str(value)
                    report += f"| {name} | {value_str} |\n"

        # 应用领域
        applications = self.product_info.get('applications', [])
        report += f"\n## 三、应用领域\n\n"
        for app in applications:
            report += f"- {app}\n"

        # 主要特性
        features = self.product_info.get('features', [])
        report += f"\n## 四、主要特性\n\n"
        for feature in features:
            report += f"✓ {feature}\n"

        # 测试项目
        report += f"\n## 五、推荐测试项目\n\n"
        report += "| 测试项 | 优先级 | 描述 |\n|------|--------|------|\n"
        for item in self.test_items:
            priority_mark = '🔴' if item['priority'] == '高' else '🟡' if item['priority'] == '中' else '🟢'
            report += f"| {item['name']} | {priority_mark} {item['priority']} | {item['description']} |\n"

        # 下一步行动
        report += f"""
---

## 六、下一步行动

1. ✅ 确认产品应用方向：**{applications[0] if applications else '待确认'}**
2. ⏳ 准备测试环境与物料
3. ⏳ 执行测试项目
4. ⏳ 生成测试报告
5. ⏳ 制作推广内容

---

*本报告由 Datasheet Parser 自动生成*
"""
        return report

    def _generate_test_excel(self, output_path: Path, timestamp: str):
        """生成测试清单 Excel"""
        model = self.product_info.get('model', 'unknown')

        df = pd.DataFrame(self.test_items)
        df.insert(0, '芯片型号', model)
        df.insert(1, '生成日期', datetime.now().strftime('%Y-%m-%d'))

        excel_path = output_path / f"{model}_测试清单_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False)
        print(f"✓ 生成测试清单 Excel: {excel_path}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='芯片规格书自动解析器')
    parser.add_argument('pdf_file', help='PDF 文件路径')
    parser.add_argument('--output', '-o', default='output', help='输出目录')

    args = parser.parse_args()

    if not os.path.exists(args.pdf_file):
        print(f"错误：文件不存在 - {args.pdf_file}")
        return

    # 创建解析器
    datasheet = DatasheetParser(args.pdf_file)

    # 提取文本
    datasheet.extract_text()

    # 提取产品信息
    datasheet.extract_product_info()

    # 生成测试项目
    datasheet.generate_test_items()

    # 生成报告
    report_path = datasheet.generate_report(args.output)

    print(f"\n✅ 解析完成！报告已保存至：{report_path}")


if __name__ == '__main__':
    main()
