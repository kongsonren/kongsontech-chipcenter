"""
测试环境搭建生成器 (Test Setup Generator)
功能:
1. 根据芯片型号生成测试电路图
2. 自动生成 BOM 清单 (含供应商链接)
3. 生成测试报告模板 (Excel/Markdown)
4. 生成测试步骤 SOP
5. 仪器连接指导

使用方法:
    python test_setup_generator.py --model LM2596 --type buck --output output_folder
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

try:
    import pandas as pd
except ImportError:
    print("请安装 pandas: pip install pandas")
    exit(1)


class TestSetupGenerator:
    """测试环境搭建生成器"""

    def __init__(self, model: str, chip_type: str = 'DC-DC 降压'):
        self.model = model
        self.chip_type = chip_type
        self.bom_items = []
        self.test_circuit = {}
        self.instruments_needed = []

        # 常见芯片类型的典型应用电路参数
        self.circuit_templates = self._get_circuit_templates()

    def _get_circuit_templates(self) -> dict:
        """获取典型应用电路模板"""
        return {
            'DC-DC 降压': {
                'circuit_type': 'Buck Converter',
                'typical_application': {
                    'input_voltage': '12V',
                    'output_voltage': '5V/3.3V/可调',
                    'output_current': '1A-5A',
                },
                'external_components': [
                    {'name': '输入电容', 'value': '10µF/25V', 'description': '陶瓷电容 X7R', 'qty': 1},
                    {'name': '输出电容', 'value': '22µF/10V', 'description': '陶瓷电容 X7R', 'qty': 1},
                    {'name': '电感', 'value': '33µH/5A', 'description': '功率电感 低 DCR', 'qty': 1},
                    {'name': '反馈电阻上', 'value': '10kΩ', 'description': '精度 1%', 'qty': 1},
                    {'name': '反馈电阻下', 'value': '根据 Vout 计算', 'description': '精度 1%', 'qty': 1},
                    {'name': '续流二极管', 'value': '1N5822/SS34', 'description': '肖特基二极管 3A/40V', 'qty': 1},
                ],
                'test_points': [
                    {'name': 'TP1', 'signal': 'VIN', 'description': '输入电压'},
                    {'name': 'TP2', 'signal': 'VOUT', 'description': '输出电压'},
                    {'name': 'TP3', 'signal': 'SW', 'description': '开关节点'},
                    {'name': 'TP4', 'signal': 'FB', 'description': '反馈电压'},
                    {'name': 'GND', 'signal': 'GND', 'description': '参考地'},
                ],
            },
            'LDO': {
                'circuit_type': 'LDO Regulator',
                'typical_application': {
                    'input_voltage': '5V-12V',
                    'output_voltage': '3.3V/5V/可调',
                    'output_current': '100mA-1A',
                },
                'external_components': [
                    {'name': '输入电容', 'value': '1µF/16V', 'description': '陶瓷电容', 'qty': 1},
                    {'name': '输出电容', 'value': '10µF/10V', 'description': '陶瓷电容', 'qty': 1},
                ],
                'test_points': [
                    {'name': 'TP1', 'signal': 'VIN', 'description': '输入电压'},
                    {'name': 'TP2', 'signal': 'VOUT', 'description': '输出电压'},
                    {'name': 'GND', 'signal': 'GND', 'description': '参考地'},
                ],
            },
            'LED 驱动': {
                'circuit_type': 'LED Driver',
                'typical_application': {
                    'input_voltage': '12V-24V',
                    'output_current': '350mA-1A',
                    'led_count': '3-10 串',
                },
                'external_components': [
                    {'name': '输入电容', 'value': '10µF/50V', 'description': '电解电容', 'qty': 1},
                    {'name': '电感', 'value': '47µH/2A', 'description': '功率电感', 'qty': 1},
                    {'name': '电流检测电阻', 'value': '0.5Ω/1W', 'description': '精密电阻', 'qty': 1},
                    {'name': '续流二极管', 'value': 'SS34', 'description': '肖特基二极管', 'qty': 1},
                ],
                'test_points': [
                    {'name': 'TP1', 'signal': 'VIN', 'description': '输入电压'},
                    {'name': 'TP2', 'signal': 'LED+', 'description': 'LED 阳极'},
                    {'name': 'TP3', 'signal': 'LED-', 'description': 'LED 阴极'},
                    {'name': 'TP4', 'signal': 'CS', 'description': '电流检测'},
                ],
            },
        }

    def generate_bom(self) -> List[Dict]:
        """生成 BOM 清单"""
        template = self.circuit_templates.get(self.chip_type, self.circuit_templates['DC-DC 降压'])

        # 添加芯片本身
        self.bom_items = [{
            '序号': 1,
            '名称': '芯片',
            '型号': self.model,
            '封装': '待确认',
            '数量': 5,  # 测试样品多准备
            '供应商': 'DigiKey/Mouser/立创',
            '备注': '测试样品'
        }]

        # 添加外围元件
        for i, component in enumerate(template['external_components'], start=2):
            supplier_link = self._get_supplier_link(component)
            self.bom_items.append({
                '序号': i,
                '名称': component['name'],
                '型号': component['value'],
                '封装': '-',
                '数量': component['qty'] * 5,  # 多准备余量
                '供应商': supplier_link['name'],
                '链接': supplier_link['link'],
                '备注': component['description']
            })

        # 添加测试耗材
        self.bom_items.extend([
            {'序号': len(self.bom_items) + 1, '名称': 'PCB 万能板', '型号': '8x12cm', '封装': '-', '数量': 2, '供应商': '立创', '链接': 'https://item.szlcsc.com/search.html', '备注': '洞洞板/万能板'},
            {'序号': len(self.bom_items) + 2, '名称': '排针', '型号': '2.54mm', '封装': '-', '数量': 20, '供应商': '立创', '链接': 'https://item.szlcsc.com/search.html', '备注': '测试点用'},
            {'序号': len(self.bom_items) + 3, '名称': '导线', '型号': '杜邦线', '封装': '-', '数量': 1, '供应商': '本地', '链接': '-', '备注': '公对公/公对母'},
        ])

        return self.bom_items

    def _get_supplier_link(self, component: Dict) -> Dict:
        """获取供应商链接"""
        suppliers = {
            '电容': {'name': '立创商城', 'link': 'https://item.szlcsc.com/search.html?keyword=陶瓷电容'},
            '电感': {'name': '立创商城', 'link': 'https://item.szlcsc.com/search.html?keyword=功率电感'},
            '电阻': {'name': '立创商城', 'link': 'https://item.szlcsc.com/search.html?keyword=精密电阻'},
            '二极管': {'name': '立创商城', 'link': 'https://item.szlcsc.com/search.html?keyword=肖特基二极管'},
        }

        for key, supplier in suppliers.items():
            if key in component['name']:
                return supplier

        return {'name': '立创商城', 'link': 'https://www.szlcsc.com/'}

    def generate_circuit_diagram(self) -> str:
        """生成电路图 (ASCII 艺术 + 描述)"""
        template = self.circuit_templates.get(self.chip_type, self.circuit_templates['DC-DC 降压'])

        if self.chip_type == 'DC-DC 降压':
            self.test_circuit = {
                'type': 'Buck Converter',
                'diagram': f"""
典型 Buck 降压电路连接图:

        VIN (12V)
           │
      ┌────┴────┐
      │         │
     ┌┴┐       │
     │ │ C1     │
     │ │ 10µF   │
     └┬┘       │
      │         │
      ├────┬────┤
      │    │    │
     ┌┴┐  1└─2┐ │
     │ │  │U1 │ │
     │ │  │   │ │
     └┬┘  3└─4┘ │
      │    │    │
      │    5    │
      │    │    │
     ┌┴┐   │   ┌┴┐
     │ │ L1  │ │ │ R1
     │ │ 33µH│ │ │ 10k
     └┬┘   │ └┬┘
      │    │  │
      ├────┴──┤
      │       │
     ┌┴┐     ┌┴┐
     │ │ C2  │ │ D1
     │ │ 22µF│ │ SS34
     └┬┘     └┬┘
      │       │
      ├───────┤
      │
     GND

引脚定义:
1 - VIN (输入)
2 - GND (地)
3 - SW (开关节点)
4 - FB (反馈)
5 - EN (使能)

测试点:
TP1: VIN - 输入电压
TP2: VOUT - 输出电压
TP3: SW - 开关节点 (测纹波)
TP4: FB - 反馈电压
""",
                'connections': [
                    'VIN → C1 正极 → U1 引脚 1',
                    'C1 负极 → GND',
                    'U1 引脚 3 (SW) → L1 一端 → D1 负极',
                    'L1 另一端 → C2 正极 → VOUT',
                    'C2 负极 → GND',
                    'D1 正极 → GND',
                    'U1 引脚 4 (FB) → 分压电阻 → VOUT/GND',
                    'U1 引脚 2 (GND) → GND',
                ]
            }
        else:
            self.test_circuit = {
                'type': template['circuit_type'],
                'diagram': '详细电路图请参考规格书 Typical Application Circuit 章节',
                'connections': ['请参考规格书典型应用电路']
            }

        return self.test_circuit['diagram']

    def generate_test_report_template(self) -> Dict:
        """生成测试报告模板"""
        template = {
            'header': {
                '芯片型号': self.model,
                '芯片类型': self.chip_type,
                '测试日期': '',
                '测试人员': '',
                '环境温度': '25°C',
                '测试依据': '规格书 + 企业标准',
            },
            'test_items': [],
            'conclusion': {
                '性能评价': '★★★★☆',
                '推荐指数': '待评定',
                '竞品对比': '',
                '目标客户': '',
            }
        }

        # 根据芯片类型添加测试项
        if self.chip_type == 'DC-DC 降压':
            template['test_items'] = [
                {
                    'name': '效率测试',
                    'test_condition': 'Vin=12V, Vout=5V',
                    'data_columns': ['负载率', '输入电压', '输出电压', '输出电流', '输入电流', '效率'],
                    'data_rows': [
                        ['25%', '12V', '5V', '0.75A', '', ''],
                        ['50%', '12V', '5V', '1.5A', '', ''],
                        ['75%', '12V', '5V', '2.25A', '', ''],
                        ['100%', '12V', '5V', '3A', '', ''],
                    ],
                    'standard': '效率 ≥ 85%',
                    'result': '',
                },
                {
                    'name': '线性调整率',
                    'test_condition': 'Iout=3A, Vin=9V-15V',
                    'data_columns': ['输入电压', '输出电压', '变化量'],
                    'data_rows': [
                        ['9V', '', ''],
                        ['12V', '', ''],
                        ['15V', '', ''],
                    ],
                    'standard': 'ΔVout ≤ ±2%',
                    'result': '',
                },
                {
                    'name': '负载调整率',
                    'test_condition': 'Vin=12V, Iout=0.5A-3A',
                    'data_columns': ['负载电流', '输出电压', '变化量'],
                    'data_rows': [
                        ['0.5A', '', ''],
                        ['1.5A', '', ''],
                        ['3A', '', ''],
                    ],
                    'standard': 'ΔVout ≤ ±2%',
                    'result': '',
                },
                {
                    'name': '纹波测试',
                    'test_condition': 'Vin=12V, Iout=3A, BW=20MHz',
                    'data_columns': ['Vpp (mV)'],
                    'data_rows': [['']],
                    'standard': 'Vpp ≤ 100mV',
                    'result': '',
                    'note': '需附示波器截图',
                },
                {
                    'name': '温升测试',
                    'test_condition': 'Vin=12V, Iout=3A, 1 小时',
                    'data_columns': ['初始温度', '最终温度', '温升'],
                    'data_rows': [['', '', '']],
                    'standard': '温升 ≤ 40°C',
                    'result': '',
                    'note': '需附热成像截图',
                },
            ]
        else:
            template['test_items'] = [
                {'name': '待补充', 'test_condition': '', 'data_columns': ['项目', '实测值'], 'data_rows': [['', '']], 'standard': '', 'result': ''}
            ]

        return template

    def generate_sop(self) -> str:
        """生成测试步骤 SOP"""
        sop = f"""# {self.model} 测试作业指导书 (SOP)

**芯片类型**: {self.chip_type}
**编写日期**: {datetime.now().strftime('%Y-%m-%d')}
**版本**: V1.0

---

## 一、测试前准备

### 1.1 物料准备
- [ ] 芯片样品 ×5
- [ ] PCB 万能板 ×2
- [ ] 外围元件 (参考 BOM 清单)
- [ ] 导线/排针若干

### 1.2 仪器准备
- [ ] 直流电源 (0-30V, 3A)
- [ ] 电子负载 (0-5A)
- [ ] 数字万用表 ×2
- [ ] 示波器 (带宽 ≥ 100MHz)
- [ ] 温枪或热电偶

### 1.3 环境准备
- [ ] 防静电工作台
- [ ] 通风良好
- [ ] 环境温度 25±5°C

---

## 二、电路搭建步骤

### 2.1 PCB 布局要点
1. 输入电容尽量靠近芯片 VIN 引脚
2. SW 节点面积尽量小
3. 反馈走线远离 SW 节点
4. 输出电容靠近负载端

### 2.2 焊接顺序
1. 焊接芯片 (注意引脚 1 方向)
2. 焊接外围阻容元件
3. 焊接电感/二极管
4. 焊接测试排针
5. 目检 + 万用表通断测试

### 2.3 上电前检查
- [ ] VIN 对 GND 无短路
- [ ] VOUT 对 GND 无短路
- [ ] 芯片引脚无连焊
- [ ] 极性元件方向正确

---

## 三、测试步骤

### 3.1 效率测试
1. 连接输入电源，设置 Vin=12V
2. 连接电子负载，设置恒流模式
3. 分别设置负载为 25%/50%/75%/100%
4. 记录每组 Vin, Iin, Vout, Iout
5. 计算效率：η = (Vout×Iout) / (Vin×Iin) × 100%

### 3.2 线性调整率测试
1. 固定负载 Iout=3A
2. 调节输入电压：9V → 12V → 15V
3. 记录每个 Vin 对应的 Vout
4. 计算：线性调整率 = (Vout_max - Vout_min) / Vout_nominal × 100%

### 3.3 负载调整率测试
1. 固定输入 Vin=12V
2. 调节负载：0.5A → 1.5A → 3A
3. 记录每个 Iout 对应的 Vout
4. 计算：负载调整率 = (Vout_max - Vout_min) / Vout_nominal × 100%

### 3.4 纹波测试
1. 示波器设置：带宽限制 20MHz, 耦合方式 AC
2. 探头使用接地弹簧 (不用接地夹)
3. 测量 VOUT 对 GND 的纹波电压 Vpp
4. 保存示波器截图

### 3.5 温升测试
1. 初始温度测量 (温枪测芯片表面)
2. 设置 Vin=12V, Iout=3A
3. 运行 1 小时，每 10 分钟记录一次温度
4. 记录最终稳定温度
5. 计算温升：ΔT = T_final - T_initial

---

## 四、数据记录

请使用 Excel 模板《{self.model}_测试报告模板.xlsx》记录所有测试数据

---

## 五、注意事项

⚠️ **安全警示**:
1. 上电时不要触摸电路板
2. 注意仪器量程，避免过流损坏
3. 纹波测试使用接地弹簧，避免接地夹引入噪声
4. 温升测试注意通风散热

⚠️ **数据准确性**:
1. 每组数据稳定 30 秒后再记录
2. 纹波测试探头尽量短
3. 温度测量点保持一致

---

## 六、常见问题

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| 无输出电压 | 芯片损坏/接线错误 | 检查接线/更换芯片 |
| 效率偏低 | 电感 DCR 大/二极管压降大 | 更换低 DCR 电感/低 Vf 二极管 |
| 纹波偏大 | 输出电容 ESR 大 | 并联陶瓷电容 |
| 温升过高 | 负载过大/散热不良 | 减小负载/加散热片 |

---

*本 SOP 由 Test Setup Generator 自动生成*
"""
        return sop

    def generate_instrument_guide(self) -> str:
        """生成仪器连接指导"""
        guide = f"""# {self.model} 测试仪器连接指南

## 一、所需仪器清单

| 仪器 | 型号要求 | 数量 | 用途 |
|------|----------|------|------|
| 直流电源 | 0-30V, 3A | 1 台 | 输入供电 |
| 电子负载 | 0-5A, 恒流模式 | 1 台 | 负载模拟 |
| 数字万用表 | 4 位半 | 2 台 | 电压/电流测量 |
| 示波器 | 带宽≥100MHz | 1 台 | 纹波/瞬态测试 |
| 温枪 | - | 1 个 | 温度测量 |

## 二、仪器连接图

```
         ┌─────────────┐
         │  直流电源   │
         │  (0-30V)    │
         └──────┬──────┘
                │ VIN
         ┌──────┴──────┐
         │  测试电路板  │
         │   {self.model}  │
         └──────┬──────┘
                │ VOUT
         ┌──────┴──────┐
         │  电子负载   │
         │  (恒流模式)  │
         └─────────────┘

电压测量:
万用表 1 → VIN (监测输入电压)
万用表 2 → VOUT (监测输出电压)

纹波测量:
示波器探头 → VOUT 测试点
接地弹簧 → GND 测试点
```

## 三、仪器设置

### 3.1 直流电源设置
- 电压模式：12V (或根据测试需求)
- 电流限制：3A
- 输出：ON

### 3.2 电子负载设置
- 模式：恒流 (CC)
- 电流：根据测试点设置 (0.75A/1.5A/2.25A/3A)
- 输入：ON

### 3.3 万用表设置
- 功能：直流电压 (DCV)
- 量程：自动或 20V
- 输入阻抗：10MΩ

### 3.4 示波器设置
- 耦合方式：AC
- 带宽限制：20MHz ON
- 时基：1ms/div (纹波测试)
- 垂直：50mV/div (纹波测试)
- 触发：边沿触发，自动

## 四、SCPI 控制指令 (可选)

如果使用可编程仪器，可使用以下 SCPI 指令:

### 电源控制
```
VOLT 12          # 设置电压 12V
CURR 3           # 设置电流限制 3A
OUTP ON          # 打开输出
MEAS:VOLT?       # 查询输出电压
MEAS:CURR?       # 查询输出电流
```

### 电子负载控制
```
MODE CC          # 恒流模式
CURR 1.5         # 设置电流 1.5A
INP ON           # 打开输入
MEAS:VOLT?       # 查询输入电压
MEAS:CURR?       # 查询输入电流
```

### 万用表控制
```
CONF:VOLT:DC     # 直流电压测量
TRIG:AUTO        # 自动触发
READ?            # 读取测量值
```
"""
        return guide

    def export_all(self, output_dir: str = 'output') -> Dict[str, str]:
        """导出所有文档"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_safe = self.model.replace('/', '_')

        exported_files = {}

        # 1. BOM 清单 Excel
        if not self.bom_items:
            self.generate_bom()

        df = pd.DataFrame(self.bom_items)
        bom_path = output_path / f"{model_safe}_BOM 清单_{timestamp}.xlsx"
        df.to_excel(bom_path, index=False)
        exported_files['bom'] = str(bom_path)

        # 2. 电路图 (Markdown)
        circuit_path = output_path / f"{model_safe}_电路图_{timestamp}.md"
        with open(circuit_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_circuit_diagram())
        exported_files['circuit'] = str(circuit_path)

        # 3. 测试报告模板 (JSON + Excel)
        report_template = self.generate_test_report_template()

        # JSON 格式
        json_path = output_path / f"{model_safe}_测试报告模板_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_template, f, ensure_ascii=False, indent=2)
        exported_files['report_json'] = str(json_path)

        # Excel 格式 (简化版)
        test_data = []
        for item in report_template['test_items']:
            test_data.append({
                '测试项': item['name'],
                '测试条件': item['test_condition'],
                '标准': item['standard'],
                '结果': '',
            })

        excel_path = output_path / f"{model_safe}_测试报告模板_{timestamp}.xlsx"
        pd.DataFrame(test_data).to_excel(excel_path, index=False)
        exported_files['report_excel'] = str(excel_path)

        # 4. 测试 SOP
        sop_path = output_path / f"{model_safe}_测试 SOP_{timestamp}.md"
        with open(sop_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_sop())
        exported_files['sop'] = str(sop_path)

        # 5. 仪器连接指导
        instrument_path = output_path / f"{model_safe}_仪器指南_{timestamp}.md"
        with open(instrument_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_instrument_guide())
        exported_files['instrument'] = str(instrument_path)

        # 6. 汇总说明文件
        readme_content = f"""# {self.model} 测试文件包

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 文件清单

1. **BOM 清单** - `{exported_files['bom']}`
   - 所有测试物料清单，含供应商链接

2. **电路图** - `{exported_files['circuit']}`
   - 典型应用电路 ASCII 图
   - 引脚定义与测试点说明

3. **测试报告模板** - `{exported_files['report_excel']}`
   - Excel 格式测试报告模板
   - 包含所有测试项目与标准

4. **测试 SOP** - `{exported_files['sop']}`
   - 详细测试步骤指导
   - 安全注意事项
   - 常见问题解答

5. **仪器指南** - `{exported_files['instrument']}`
   - 仪器连接图
   - 仪器设置参数
   - SCPI 控制指令

## 使用流程

1. 打印 BOM 清单 → 采购物料
2. 查看电路图 → 理解电路原理
3. 阅读 SOP → 准备测试环境
4. 按照仪器指南 → 连接测试设备
5. 执行测试 → 填写报告模板
6. 保存数据 → 进入下一环节 (内容生成)

---
*此文件包由 Test Setup Generator 自动生成*
"""
        readme_path = output_path / f"{model_safe}_README_{timestamp}.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        exported_files['readme'] = str(readme_path)

        return exported_files


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='测试环境搭建生成器')
    parser.add_argument('--model', '-m', required=True, help='芯片型号')
    parser.add_argument('--type', '-t', default='DC-DC 降压', help='芯片类型')
    parser.add_argument('--output', '-o', default='output', help='输出目录')

    args = parser.parse_args()

    print(f"正在生成 {args.model} ({args.type}) 的测试环境文件...")

    # 创建生成器
    generator = TestSetupGenerator(args.model, args.type)

    # 生成 BOM
    generator.generate_bom()

    # 生成电路图
    generator.generate_circuit_diagram()

    # 导出所有文件
    exported_files = generator.export_all(args.output)

    print(f"\n✅ 生成完成！共导出 {len(exported_files)} 个文件:")
    for file_type, path in exported_files.items():
        print(f"  ✓ {file_type}: {path}")

    print(f"\n下一步：按照 README 文件指引开始测试准备")


if __name__ == '__main__':
    main()
