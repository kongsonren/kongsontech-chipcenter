"""
内容生成自动化脚本 (Content Generator)
功能:
1. 基于测试数据生成视频脚本 (30 秒)
2. 生成知乎技术文章
3. 生成公众号推文
4. 生成 B 站视频简介
5. 生成朋友圈文案
6. 生成 1688 产品详情页

使用方法:
    python content_generator.py --model LM2596 --test-data test_report.json --output output_folder
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class ContentGenerator:
    """内容生成器"""

    def __init__(self, model: str, test_data: Dict = None):
        self.model = model
        self.test_data = test_data or {}
        self.content_cache = {}

    def generate_video_script(self, duration: int = 30) -> str:
        """
        生成 30 秒产品视频脚本

        结构:
        - 0-5 秒：产品展示 (吸引注意)
        - 5-15 秒：测试数据展示 (建立信任)
        - 15-25 秒：应用场景 (激发需求)
        - 25-30 秒：行动号召 (引导转化)
        """
        # 从测试数据提取亮点
        efficiency = self.test_data.get('efficiency', '91%')
        temp_rise = self.test_data.get('temp_rise', '35°C')
        ripple = self.test_data.get('ripple', '80mV')
        chip_type = self.test_data.get('chip_type', 'DC-DC 芯片')

        script = f"""# {self.model} 产品视频脚本 (30 秒)

**产品类型**: {chip_type}
**视频时长**: {duration}秒
**拍摄日期**: {datetime.now().strftime('%Y-%m-%d')}

---

## 分镜头脚本

### 【镜头 1】(0-5 秒) - 产品展示 🔥

**画面**:
- 芯片特写镜头 (微距拍摄)
- 测试板全景展示
- 字幕弹出

**字幕**:
> {self.model} 实测，效率超{efficiency}!

**配音** (可选):
> "找电源芯片？看这款!"

**BGM**: 轻快节奏音乐起

---

### 【镜头 2】(5-15 秒) - 测试数据展示 📊

**画面**:
- 示波器纹波波形 (动态展示)
- 效率曲线图 (柱状图)
- 万用表读数特写
- 热成像仪温度显示

**字幕** (逐条弹出):
> 满载 3A 输出，效率{efficiency}
> 输出纹波 < {ripple}
> 满载温升仅{temp_rise}

**配音**:
> "输入 12V 转 5V，满载 3A 输出，
> 效率高达{efficiency}，温升仅{temp_rise}，
> 纹波低于{ripple}，性能稳定可靠!"

**BGM**: 音乐节奏加强

---

### 【镜头 3】(15-25 秒) - 应用场景 💡

**画面**:
- LED 驱动电源实物 (或产品渲染图)
- 车载充电器应用
- 工业控制板应用
- 快速切换场景

**字幕**:
> 适用于：
> ✓ LED 驱动电源
> ✓ 车载充电器
> ✓ 工业控制板
> ✓ 智能家居设备

**配音**:
> "广泛应用于 LED 驱动、车载充电、
> 工业控制、智能家居等多个领域，
> 是您电源设计的可靠选择!"

**BGM**: 音乐高潮

---

### 【镜头 4】(25-30 秒) - 行动号召 🎯

**画面**:
- 公司 Logo/联系方式
- 微信二维码
- 1688 店铺二维码

**字幕**:
> 现货供应 | 免费样品 | 技术支持
> 私信获取样品，48 小时发货
> 微信：[您的微信号]

**配音**:
> "现在咨询，免费提供样品和测试报告，
> 48 小时快速发货，欢迎私信!"

**BGM**: 音乐渐弱

---

## 拍摄建议

### 设备准备
- 相机/手机：1080P 以上，60fps
- 微距镜头：拍摄芯片细节
- 三脚架：保持稳定
- 补光灯：确保光线充足

### 拍摄技巧
1. 芯片特写：45 度角，突出型号标识
2. 测试数据：屏幕录制 + 实景结合
3. 应用场景：实物展示或 3D 渲染
4. 转场：快速切换，保持节奏感

### 后期制作
- 软件：剪映/PR/FCP
- 字幕：白色字体，黑色描边
- 调色：科技蓝/活力橙
- 时长控制：严格 30 秒

---

## 多平台适配

| 平台 | 画幅 | 时长 | 备注 |
|------|------|------|------|
| 抖音/快手 | 9:16 竖屏 | 30 秒 | 主战场 |
| B 站 | 16:9 横屏 | 30-60 秒 | 可延长 |
| 视频号 | 9:16 竖屏 | 30 秒 | 同步抖音 |
| 知乎视频 | 16:9 横屏 | 30 秒 | 技术向 |

---

*本脚本由 Content Generator 自动生成*
"""
        self.content_cache['video_script'] = script
        return script

    def generate_zhihu_article(self) -> str:
        """
        生成知乎技术文章

        结构:
        - 开头：痛点引入 (吸引目标读者)
        - 正文：专业分析 (建立专业度)
        - 案例：实际案例 (建立信任)
        - 结尾：引导转化 (私信/加微信)
        """
        chip_type = self.test_data.get('chip_type', 'DC-DC 芯片')
        efficiency = self.test_data.get('efficiency', '91%')
        temp_rise = self.test_data.get('temp_rise', '35°C')

        article = f"""# 实测 {self.model}，这款{chip_type}还能打吗？

**作者**: [您的知乎名]
**发布时间**: {datetime.now().strftime('%Y-%m-%d')}
**阅读时间**: 约 5 分钟

---

## 开头：选型痛点

> 最近很多工程师朋友私信问：
>
> "做 LED 驱动电源，市面上{chip_type}几十种，
> TI 的{self.model}、MPS 的 MP2596、国产的 XL2596...
> 到底怎么选？哪款性价比最高？"
>
> 刚好手上有TI 的{self.model}样品，今天就来一期实测，
> 用数据说话，看看这款经典芯片现在还能不能打！

![产品图](图片占位：芯片 + 测试板合影)

---

## 一、外观与封装

先看看{self.model}的基本信息：

| 参数 | 规格 |
|------|------|
| 型号 | {self.model} |
| 类型 | {chip_type} |
| 封装 | TO-220 / TO-263 |
| 输入电压 | 4.5V-40V |
| 输出电流 | 3A |
| 开关频率 | 150kHz |

![封装图](图片占位：芯片封装特写)

实物拿到手第一感觉：做工扎实，引脚镀层均匀，
丝印清晰，大厂品质没得说。

---

## 二、测试环境与仪器

### 测试电路

按照规格书典型应用电路搭建：
- 输入：12V
- 输出：5V/3A
- 外围元件：按规格书推荐值

![电路图](图片占位：测试电路原理图)

### 测试仪器

| 仪器 | 型号 | 用途 |
|------|------|------|
| 直流电源 | Rigol DP832 | 输入供电 |
| 电子负载 | ITECH IT8511 | 负载模拟 |
| 万用表 | Fluke 17B+ | 电压/电流测量 |
| 示波器 | Rigol DS1054Z | 纹波/瞬态测试 |
| 温枪 | 工业级 | 温度测量 |

---

## 三、效率实测

### 测试条件
- 输入电压：12V
- 输出电压：5V
- 负载点：25% / 50% / 75% / 100%

### 测试数据

| 负载率 | 输入电压 | 输出电压 | 输出电流 | 输入电流 | 效率 |
|--------|----------|----------|----------|----------|------|
| 25%    | 12V      | 5.01V    | 0.75A    | 0.21A    | {efficiency} |
| 50%    | 12V      | 5.00V    | 1.50A    | 0.42A    | {efficiency} |
| 75%    | 12V      | 4.99V    | 2.25A    | 0.64A    | 89% |
| 100%   | 12V      | 4.98V    | 3.00A    | 0.87A    | 87% |

![效率曲线](图片占位：效率 vs 负载率 曲线图)

### 分析

从数据可以看出：
1. **轻载效率高**: 25% 负载时效率达到{efficiency}，适合待机应用
2. **满载效率稳定**: 100% 负载仍有 87%，优于同级别产品
3. **整体表现**: 平均效率超过 89%，符合预期

---

## 四、纹波与噪声测试

### 测试条件
- 示波器带宽限制：20MHz
- 探头：使用接地弹簧 (不用接地夹)
- 耦合方式：AC

### 测试结果

![纹波波形](图片占位：示波器纹波截图)

**实测纹波**: < 80mVpp

这个表现在{chip_type}中属于**优秀水平**，
完全可以满足对电源噪声敏感的应用场景。

---

## 五、温升测试

### 测试方法
- 环境条件：25°C 室温，无风道
- 负载条件：满载 3A 持续运行 1 小时
- 测量点：芯片表面 (使用温枪)

### 测试结果

| 时间 | 温度 | 温升 |
|------|------|------|
| 初始 | 25°C | - |
| 10min | 42°C | +17°C |
| 30min | 55°C | +30°C |
| 60min | 60°C | +35°C |

![热成像](图片占位：热成像温度分布图)

**满载 1 小时温升**: {temp_rise}

这个温升表现在 TO-220 封装中属于**正常水平**，
建议实际应用时加装配散热片。

---

## 六、竞品对比

为了更直观，我拉了三款同级别产品对比：

| 型号 | 效率 (满载) | 纹波 | 温升 | 单价 |
|------|-------------|------|------|------|
| TI {self.model} | 87% | 80mV | 35°C | ¥2.5 |
| MPS MP2596 | 84% | 95mV | 42°C | ¥2.3 |
| 国产 XL2596 | 82% | 120mV | 48°C | ¥1.8 |

### 结论

- **性能**: TI 原厂 > MPS > 国产
- **价格**: 国产 > MPS > TI
- **性价比**: 看应用场景
  - 高可靠性场景 (汽车/医疗/工业) → 推荐 TI 原厂
  - 消费电子/成本敏感 → 可以考虑国产

---

## 七、实际应用案例

上个月帮深圳一家 LED 驱动客户解决了个问题：

**客户痛点**:
- 原方案用某国产芯片，效率只有 80%
- 满载温升超过 60°C，客户担心可靠性
- 出口产品，需要通过 CE/FCC 认证

**解决方案**:
- 推荐客户改用 TI {self.model}
- 优化 PCB 布局 (输入电容靠近芯片，减小 SW 面积)
- 加装配小型散热片

**改善效果**:
- 效率从 80% 提升到 87%
- 温升降低 25°C
- 纹波从 150mV 降低到 80mV
- 顺利通过 CE 认证

客户反馈：虽然芯片成本贵了 0.7 元，
但整体 BOM 成本反而降低了 (散热片减小、EMI 器件减少),
而且可靠性大幅提升，售后问题减少 80%。

---

## 八、选型建议

### 推荐用{self.model}的场景
✅ 对效率有要求 (>85%)
✅ 工作环境温度高
✅ 需要通过安规认证
✅ 批量生产，重视可靠性

### 可以考虑替代品的场景
⭕ 成本极度敏感 (如玩具、低端消费电子)
⭕ 小批量打样 (国产芯片货期更短)
⭕ 对效率/温升不敏感的应用

---

## 九、总结

经过一周的实测，我对 TI {self.model}的评价：

**综合评分**: ⭐⭐⭐⭐☆ (4.2/5)

| 维度 | 评分 | 说明 |
|------|------|------|
| 性能 | ⭐⭐⭐⭐⭐ | 效率/纹波/温升都表现优秀 |
| 价格 | ⭐⭐⭐⭐ | 原厂芯片中性价比高 |
| 货期 | ⭐⭐⭐ | 需要关注库存情况 |
| 技术支持 | ⭐⭐⭐⭐⭐ | TI 官网资料齐全 |

**购买建议**:
- 样品申请：TI 官网/授权代理商
- 小批量：立创商城/云汉芯城
- 大批量：联系 TI 销售

---

## 十、福利时间 🎁

看到这里的都是真爱粉，给大家准备点福利：

1️⃣ **免费样品**:
   需要{self.model}样品测试的朋友，
   可以私信我，免费提供 3pcs 样品 (付邮费即可)

2️⃣ **测试报告**:
   关注我并私信"选型"，
   发送完整版测试报告 (含原始数据)

3️⃣ **技术咨询**:
   有任何电源设计问题，
   欢迎评论区留言或私信交流

4️⃣ **微信交流群**:
   想和更多工程师交流？
   添加微信：[您的微信号]
   备注"知乎进群"，拉你进电源技术交流群

---

**下期预告**:
下期实测 MPS MP2596，
和 TI {self.model}对比，看看谁更值得选？
关注我，不迷路！

---

**标签**:
#芯片选型 #电源设计 #硬件工程 #LED 驱动 #电子工程师

---

*本文所有测试数据均为实测，仅供参考。*
*如有错误，欢迎评论区指正。*
"""
        self.content_cache['zhihu_article'] = article
        return article

    def generate_wechat_article(self) -> str:
        """
        生成公众号推文

        特点:
        - 篇幅适中 (800-1200 字)
        - 图文结合
        - 引导关注/转发
        """
        # 从测试数据提取关键参数
        eff_val = self.test_data.get('efficiency', '87%')
        temp_val = self.test_data.get('temp_rise', '35°C')
        ripple_val = self.test_data.get('ripple', '80mVpp')
        chip_val = self.test_data.get('chip_type', 'DC-DC 芯片')

        article = f"""# 【实测】{self.model}性能大揭秘！效率竟高达...

![头图](图片占位：产品测试场景图)

> **导读**:
> 电源芯片怎么选？实测数据告诉你答案！
> 今天给大家带来 TI 经典款{self.model}的完整测试报告，
> 效率、纹波、温升...一项都不漏！

---

## 🔍 为什么测这款芯片？

最近很多粉丝问：
"做电源设计，TI/MPS/国产芯片，到底怎么选？"

光看规格书可不行，**实测才是硬道理**!

这周我们把 TI {self.model}拉来实测，
用数据说话，看看这款经典芯片表现如何！

---

## 📊 测试数据抢先看

### 效率测试

满载 3A 输出，效率达到**87%**!
轻载{eff_val},待机功耗优秀!

![效率曲线](图片占位：效率曲线图)

### 纹波测试

实测输出纹波 **< 80mVpp**
在同类产品中属于**优秀水平**!

![纹波波形](图片占位：纹波波形图)

### 温升测试

满载 1 小时，温升仅**{temp_val}**
配合散热片，高温环境也稳定!

![热成像](图片占位：热成像图)

---

## 💡 应用场景推荐

这款芯片适合：
✓ LED 驱动电源
✓ 车载充电器
✓ 工业控制板
✓ 智能家居设备

特别是**对效率和可靠性有要求**的场景，
强烈推荐用这款!

---

## 🎁 粉丝福利

需要样品的朋友看过来！

**福利 1**: 免费申请样品
👉 关注公众号，回复"{self.model}"
👉 获取免费样品申请方式 (仅需付邮费)

**福利 2**: 完整测试报告
👉 回复"测试报告"
👉 获取 PDF 版本完整报告 (含原始数据)

**福利 3**: 技术交流群
👉 添加小编微信：[您的微信号]
👉 备注"进群"
👉 拉你进电源技术交流群，和数百位工程师一起交流

---

## 📌 下期预告

下期我们将实测 MPS MP2596，
和 TI {self.model}正面 PK!
谁能胜出？敬请期待!

**关注我，不迷路!** 👇

![二维码](图片占位：公众号二维码)

---

**往期精选**:
- [文章 1 链接]
- [文章 2 链接]
- [文章 3 链接]

---

**版权声明**: 本文测试数据均为实测，转载请注明出处。
"""
        self.content_cache['wechat_article'] = article
        return article

    def generate_bilibili_description(self) -> str:
        """生成 B 站视频简介"""
        description = f"""# {self.model} 完整测试报告 | 效率/纹波/温升实测数据公开

🔬 **测试周期**: 1 周
📊 **测试项目**: 效率/纹波/温升/负载调整率
🎯 **适合人群**: 硬件工程师/电源工程师/电子爱好者

---

## ⏱️ 视频目录

00:00 开场介绍
00:30 芯片外观展示
01:00 测试环境搭建
02:00 效率实测
03:30 纹波测试
04:30 温升测试
05:30 数据总结
06:00 福利时间

---

## 📋 重点数据

✅ 满载效率：87%
✅ 输出纹波：< 80mVpp
✅ 满载温升：35°C
✅ 推荐指数：⭐⭐⭐⭐☆

---

## 💬 互动福利

1. **免费样品**: 评论区留言"{self.model}",抽 3 位粉丝送免费样品
2. **测试报告**: 私信我"报告",获取完整版测试数据
3. **技术咨询**: 有任何电源问题，评论区见!

---

## 🔗 相关资源

- 规格书下载：[链接]
- 测试报告下载：[链接]
- 样品申请：[链接]

---

## 🏷️ Tags

#{self.model} #电源芯片 #硬件设计 #电子工程师 #芯片评测 #电源设计 #LED 驱动 #测试报告

---

**关注我**,更多芯片实测干货持续更新!
"""
        self.content_cache['bilibili_description'] = description
        return description

    def generate_wechat_moments(self) -> List[str]:
        """生成朋友圈文案 (5 条)"""
        moments = [
            f"""【新品测试】{self.model} 完整测试报告出炉!🔬
效率 87%,纹波<80mV,温升 35°C
数据不会说谎，这款真的可以冲!
需要样品的私信我，免费安排~ 📦
[图片 9 宫格：测试场景 + 数据图表]""",

            f"""帮深圳客户解决了一个电源难题!💡
原方案效率 80%,温升 60°C+
换成{self.model}后:
✓ 效率提升到 87%
✓ 温升降低 25°C
✓ 成本反而下降
选对芯片，真的可以事半功倍!
有类似问题的朋友，欢迎交流~ 🤝""",

            f"""【技术分享】电源芯片选型的 5 个关键点
1️⃣ 效率 (影响温升和可靠性)
2️⃣ 纹波 (影响后端电路稳定性)
3️⃣ 负载调整率 (动态响应能力)
4️⃣ 保护功能 (过流/过压/过热)
5️⃣ 性价比 (不是越便宜越好)
今天实测的{self.model},5 项全过! ✅
详细报告私信我领取~ 📊""",

            f"""周末还在实验室测芯片，我是不是太卷了？😅
不过看到{self.model}这效率数据，值了!
做技术就是这样，数据不会陪你演戏~
工程师朋友们，周末愉快! 💪
[图片：实验室夜景]""",

            f"""【客户反馈】上周发的样品，今天收到反馈:
"效率确实高，温升也控制得不错，
关键是技术支持到位，响应快!"
这就是我们坚持做测试报告的意义!
用数据说话，用产品证明! 👍
需要电源方案的朋友，随时联系~ 📱""",
        ]
        self.content_cache['wechat_moments'] = moments
        return moments

    def generate_1688_detail_page(self) -> str:
        """生成 1688 产品详情页 HTML"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{self.model} 产品详情</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .section {{ margin: 30px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; }}
        .section-title {{ font-size: 20px; font-weight: bold; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .feature {{ display: inline-block; background: #f0f4ff; padding: 10px 20px; margin: 10px; border-radius: 20px; color: #667eea; font-weight: bold; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
        .data-table th {{ background: #f8f9fa; font-weight: bold; }}
        .highlight {{ background: #fff3cd; padding: 5px 10px; border-radius: 4px; }}
        .application {{ text-align: center; margin: 20px 0; }}
        .cta {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; text-align: center; border-radius: 8px; margin-top: 30px; }}
        .cta-button {{ display: inline-block; background: white; color: #f5576c; padding: 12px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; margin: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.model}</h1>
        <p>高性能 {self.test_data.get('chip_type', 'DC-DC 芯片')} | 原厂正品 | 现货供应</p>
    </div>

    <div class="section">
        <div class="section-title">🏆 产品亮点</div>
        <div class="feature">✓ 效率高 ({self.test_data.get('efficiency', '91%')})</div>
        <div class="feature">✓ 温升低 ({self.test_data.get('temp_rise', '35°C')})</div>
        <div class="feature">✓ 纹波小 (< {self.test_data.get('ripple', '80mV')})</div>
        <div class="feature">✓ 原厂正品</div>
        <div class="feature">✓ 现货供应</div>
        <div class="feature">✓ 技术支持</div>
    </div>

    <div class="section">
        <div class="section-title">📊 实测数据</div>
        <table class="data-table">
            <tr>
                <th>测试项目</th>
                <th>测试条件</th>
                <th>实测结果</th>
                <th>行业标准</th>
            </tr>
            <tr>
                <td class="highlight">效率</td>
                <td>12V 转 5V, 满载 3A</td>
                <td class="highlight">{self.test_data.get('efficiency', '87%')}</td>
                <td>≥85%</td>
            </tr>
            <tr>
                <td>输出纹波</td>
                <td>满载 3A, BW=20MHz</td>
                <td>&lt; {self.test_data.get('ripple', '80mV')}</td>
                <td>&lt;100mV</td>
            </tr>
            <tr>
                <td>温升测试</td>
                <td>满载 1 小时</td>
                <td>{self.test_data.get('temp_rise', '35°C')}</td>
                <td>&lt;40°C</td>
            </tr>
            <tr>
                <td>负载调整率</td>
                <td>0.5A-3A</td>
                <td>±1.5%</td>
                <td>±2%</td>
            </tr>
        </table>
        <p style="text-align: center; color: #666;">*所有数据均为实测，支持第三方复检</p>
    </div>

    <div class="section">
        <div class="section-title">💡 应用场景</div>
        <div class="application">
            <p><strong>推荐应用:</strong></p>
            <p>✓ LED 驱动电源 &nbsp;&nbsp; ✓ 车载充电器 &nbsp;&nbsp; ✓ 工业控制板</p>
            <p>✓ 智能家居设备 &nbsp;&nbsp; ✓ 安防监控 &nbsp;&nbsp; ✓ 网络设备</p>
            <p>✓ 医疗设备 &nbsp;&nbsp; ✓ 仪器仪表 &nbsp;&nbsp; ✓ 通信设备</p>
        </div>
    </div>

    <div class="section">
        <div class="section-title">📦 供货信息</div>
        <table class="data-table">
            <tr>
                <th>型号</th>
                <td>{self.model}</td>
            </tr>
            <tr>
                <th>品牌</th>
                <td>TI (德州仪器)</td>
            </tr>
            <tr>
                <th>封装</th>
                <td>TO-220 / TO-263</td>
            </tr>
            <tr>
                <th>起订量</th>
                <td>1pcs (样品支持)</td>
            </tr>
            <tr>
                <th>货期</th>
                <td>现货，当天发货</td>
            </tr>
            <tr>
                <th>价格</th>
                <td>询价 (量大从优)</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <div class="section-title">🎁 增值服务</div>
        <p><strong>1. 免费样品:</strong> 支持 1-3pcs 样品测试 (付邮费即可)</p>
        <p><strong>2. 技术支持:</strong> 专业工程师一对一技术支持</p>
        <p><strong>3. 测试报告:</strong> 提供完整测试报告</p>
        <p><strong>4. 替代方案:</strong> 根据需求推荐最优性价比方案</p>
        <p><strong>5. 账期支持:</strong> 老客户可申请月结账期</p>
    </div>

    <div class="cta">
        <h2>🎯 立即咨询，获取免费样品!</h2>
        <p>专业团队，快速响应，48 小时发货</p>
        <a href="#" class="cta-button">💬 立即咨询</a>
        <a href="#" class="cta-button">📞 电话联系</a>
        <a href="#" class="cta-button">📱 添加微信</a>
    </div>
</body>
</html>
"""
        self.content_cache['1688_detail'] = html
        return html

    def export_all(self, output_dir: str = 'output') -> Dict[str, str]:
        """导出所有内容"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_safe = self.model.replace('/', '_')

        exported_files = {}

        # 1. 视频脚本
        video_script = self.generate_video_script()
        video_path = output_path / f"{model_safe}_视频脚本_{timestamp}.md"
        with open(video_path, 'w', encoding='utf-8') as f:
            f.write(video_script)
        exported_files['video_script'] = str(video_path)

        # 2. 知乎文章
        zhihu = self.generate_zhihu_article()
        zhihu_path = output_path / f"{model_safe}_知乎文章_{timestamp}.md"
        with open(zhihu_path, 'w', encoding='utf-8') as f:
            f.write(zhihu)
        exported_files['zhihu'] = str(zhihu_path)

        # 3. 公众号文章
        wechat = self.generate_wechat_article()
        wechat_path = output_path / f"{model_safe}_公众号文章_{timestamp}.md"
        with open(wechat_path, 'w', encoding='utf-8') as f:
            f.write(wechat)
        exported_files['wechat'] = str(wechat_path)

        # 4. B 站简介
        bilibili = self.generate_bilibili_description()
        bilibili_path = output_path / f"{model_safe}_B 站简介_{timestamp}.md"
        with open(bilibili_path, 'w', encoding='utf-8') as f:
            f.write(bilibili)
        exported_files['bilibili'] = str(bilibili_path)

        # 5. 朋友圈文案
        moments = self.generate_wechat_moments()
        moments_path = output_path / f"{model_safe}_朋友圈文案_{timestamp}.txt"
        with open(moments_path, 'w', encoding='utf-8') as f:
            for i, moment in enumerate(moments, 1):
                f.write(f"【文案{i}】\n{moment}\n\n{'='*50}\n\n")
        exported_files['moments'] = str(moments_path)

        # 6. 1688 详情页
        detail_html = self.generate_1688_detail_page()
        detail_path = output_path / f"{model_safe}_1688 详情页_{timestamp}.html"
        with open(detail_path, 'w', encoding='utf-8') as f:
            f.write(detail_html)
        exported_files['1688_detail'] = str(detail_path)

        # 7. 内容汇总说明
        readme_content = f"""# {self.model} 内容包

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 文件清单

1. **视频脚本** - `{exported_files['video_script']}`
   - 30 秒产品视频分镜头脚本
   - 适配抖音/B 站/视频号

2. **知乎文章** - `{exported_files['zhihu']}`
   - 技术向长文 (约 3000 字)
   - 建立专业度，引流私域

3. **公众号文章** - `{exported_files['wechat']}`
   - 推文格式 (约 1000 字)
   - 引导关注/转发

4. **B 站简介** - `{exported_files['bilibili']}`
   - 视频简介 + 时间戳
   - 互动引导

5. **朋友圈文案** - `{exported_files['moments']}`
   - 5 条不同风格文案
   - 可连续发 5 天

6. **1688 详情页** - `{exported_files['1688_detail']}`
   - HTML 格式产品详情
   - 可直接用于店铺

## 使用流程

1. 拍摄视频 → 使用视频脚本
2. 发布知乎 → 复制知乎文章
3. 公众号推送 → 复制公众号文章
4. 上传 B 站 → 复制简介
5. 朋友圈运营 → 每天 1 条文案
6. 1688 上架 → 导入详情页 HTML

## 注意事项

- 文中 [您的微信号] 需替换为实际微信号
- 测试数据需根据实际测试结果修改
- 图片需自行拍摄或制作

---
*此内容包由 Content Generator 自动生成*
"""
        readme_path = output_path / f"{model_safe}_内容包说明_{timestamp}.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        exported_files['readme'] = str(readme_path)

        return exported_files


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='内容生成器')
    parser.add_argument('--model', '-m', required=True, help='芯片型号')
    parser.add_argument('--test-data', '-t', help='测试数据 JSON 文件')
    parser.add_argument('--output', '-o', default='output', help='输出目录')

    args = parser.parse_args()

    # 加载测试数据
    test_data = {}
    if args.test_data and os.path.exists(args.test_data):
        with open(args.test_data, 'r', encoding='utf-8') as f:
            test_data = json.load(f)

    print(f"正在为 {args.model} 生成推广内容...")

    # 创建生成器
    generator = ContentGenerator(args.model, test_data)

    # 导出所有内容
    exported_files = generator.export_all(args.output)

    print(f"\n✅ 生成完成！共导出 {len(exported_files)} 个文件:")
    for file_type, path in exported_files.items():
        print(f"  ✓ {file_type}: {path}")

    print(f"\n下一步：根据内容进行视频拍摄和多平台发布")


if __name__ == '__main__':
    main()
