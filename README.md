# 芯片作战指挥中心 - Chip Command Center

> **自动化运营 Dashboard by KR**
> 版本：v1.0
> 创建时间：2026-03-29
> 作者：Kongson Ren (任光成)

---

## 📖 项目介绍

**芯片作战指挥中心** 是一个面向 LED 室内照明和 RGBCW 氛围类产品的全自动化运营系统。该系统集成了 1688 选品、产品数据管理、多渠道内容生成、微信发布、数据看板等核心功能，帮助 5 人小团队实现半年内构建全自动工作流的目标。

### 🎯 项目背景

- **团队配置**：5 人（GM 1 名 + 软件工程师 1 名 + 硬件工程师 1 名 + 业务兼职美工 1 名 + 业务兼职文员 1 名）
- **办公地点**：中山古镇（灯都）+ 华强北 + 宁波
- **目标**：用半年时间打造全自动工作流，运行宜欧特灯饰商行
- **行业聚焦**：LED 室内照明、RGBCW 氛围类产品

---

## ✨ 核心功能

### 1️⃣ 1688 选品系统
- 自动爬取 1688 产品详情
- 产品数据标准化存储
- 价格分析与利润计算
- 供应商信息管理

### 2️⃣ 产品数据库管理
- SQLite 数据库存储所有产品信息
- 支持多表关联查询
- 数据去重与清洗
- 批量导入导出

### 3️⃣ 多渠道内容生成
- 自动生成产品文案
- 适配不同平台格式（微信公众号、小红书、抖音等）
- SEO 优化关键词嵌入
- 一键发布准备

### 4️⃣ 微信公众号发布
- 自动排版与发布
- 定时任务支持
- 发布历史记录
- 阅读量追踪

### 5️⃣ 数据可视化 Dashboard
- 实时销售数据看板
- 产品分布统计
- 渠道效果分析
- 运营效率监控

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 编程语言 | Python 3.10+ |
| 数据库 | SQLite |
| Web 框架 | （待添加） |
| 自动化 | Playwright / Selenium |
| 定时任务 | Windows Task Scheduler |
| 版本控制 | Git + GitHub |

---

## 📁 项目结构

```
kongsontech-chipcenter/
├── scripts/                    # 核心脚本
│   ├── database.py            # 数据库操作
│   ├── content_generator.py   # 内容生成器
│   ├── wechat_publisher.py    # 微信发布
│   ├── platform_distribution.py  # 多渠道分发
│   ├── cleanup_duplicates.py  # 数据去重
│   ├── datasheet_parser.py    # 数据手册解析
│   └── 1688_product.py        # 1688 产品爬取
├── tools/                      # 工具脚本
│   └── parse_pdf_quote.py     # PDF 报价单解析
├── data/                       # 数据目录（不提交到 Git）
│   ├── chip_workflow.db       # 主数据库
│   └── products.db            # 产品数据库
├── output/                     # 输出目录
│   ├── wechat/                # 微信发布内容
│   └── reports/               # 报告文件
├── dashboard/                  # 数据看板
│   ├── index.html             # Dashboard 首页
│   └── data/                  # 看板数据
└── README.md                   # 项目说明
```

---

## 🚀 快速开始

### 环境要求

- Windows 10/11
- Python 3.10 或更高版本
- Git

### 安装步骤

```powershell
# 1. 克隆仓库
git clone https://github.com/kongsonren/kongsontech-chipcenter.git
cd kongsontech-chipcenter

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库
python scripts/database.py --init

# 4. 测试环境
python scripts/test_setup_generator.py
```

### 配置说明

1. **环境变量配置**：复制 `.env.example` 为 `.env`（如有）
2. **数据库路径**：修改 `scripts/database.py` 中的数据库连接字符串
3. **API 密钥**：配置微信、1688 等平台的 API 密钥（如需要）

---

## 📋 使用指南

### 1688 产品爬取

```powershell
# 爬取单个产品
python scripts/1688_product.py --url <产品 URL>

# 批量爬取
python scripts/1688_product.py --batch input_urls.txt
```

### 内容生成

```powershell
# 生成产品文案
python scripts/content_generator.py --product-id <产品 ID>

# 批量生成
python scripts/content_generator.py --all
```

### 微信发布

```powershell
# 发布到微信
python scripts/wechat_publisher.py --article-id <文章 ID>

# 定时发布（使用 Windows 任务计划）
start-wechat-publisher.bat
```

### 数据清理

```powershell
# 清理重复数据
python scripts/cleanup_duplicates.py

# 解析 PDF 报价单
python tools/parse_pdf_quote.py --file quote.pdf
```

---

## 📊 数据库结构

### 核心数据表

| 表名 | 说明 |
|------|------|
| products | 产品基本信息 |
| suppliers | 供应商信息 |
| price_history | 价格历史记录 |
| content_library | 内容文案库 |
| publish_history | 发布历史记录 |
| platform_stats | 渠道统计数据 |

---

## 🎯 路线图

### 第一阶段（2026.04 - 2026.06）
- [x] 基础框架搭建
- [x] 1688 产品爬取
- [x] 数据库管理
- [ ] 内容自动生成
- [ ] 微信自动发布

### 第二阶段（2026.07 - 2026.09）
- [ ] Dashboard 数据看板
- [ ] 多渠道分发（小红书、抖音）
- [ ] 数据报表自动生成
- [ ] 移动端适配

### 第三阶段（2026.10 - 2026.12）
- [ ] AI 智能选品推荐
- [ ] 销售预测分析
- [ ] 自动化运营全流程
- [ ] 团队权限管理

---

## 📈 运营目标

| 时间 | 目标 |
|------|------|
| 2026 Q2 | 完成 1688 选品系统，积累 100+ 产品数据 |
| 2026 Q3 | 实现内容自动生成，公众号日更 |
| 2026 Q4 | Dashboard 上线，全渠道数据整合 |
| 2027 Q1 | 实现全自动工作流，5 人团队高效运行 |

---

## 🤝 团队协作

### 角色分工

| 角色 | 职责 |
|------|------|
| GM (KR) | 战略规划、资源协调 |
| 软件工程师 | 系统开发、维护 |
| 硬件工程师 | 产品测试、技术支持 |
| 业务兼职美工 | 内容美化、设计 |
| 业务兼职文员 | 数据录入、日常运营 |

### 办公地点

- **总部**：中山古镇（灯都）
- **分部**：深圳华强北、浙江宁波

---

## 📝 开发日志

- **2026-03-29**: 项目创建，初始代码推送至 GitHub
- **2026-03-30**: README.md 文档完善

---

## 📄 许可证

本项目为内部使用，未开源。

---

## 📞 联系方式

- **作者**: Kongson Ren (任光成)
- **邮箱**: （待添加）
- **GitHub**: [@kongsonren](https://github.com/kongsonren)

---

<div align="center">

**芯片作战指挥中心** | 全自动化运营 · 5 人团队 · 半年目标

🚀 *用技术驱动商业效率*

</div>
