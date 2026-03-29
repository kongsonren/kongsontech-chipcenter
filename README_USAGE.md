# 宜欧特自动化工作流 - 使用指南

## 📋 已完成的工具

### 工具 1：PDF 报价单解析器 ✅

**功能**：自动解析供应商 PDF 报价单，提取产品信息，生成 Excel 表格

**使用方法**：
```bash
# 方式 1：直接运行（自动生成输出文件名）
python tools\parse_pdf_quote.py "path\to\quote.pdf"

# 方式 2：指定输出文件名
python tools\parse_pdf_quote.py "path\to\quote.pdf" "output.xlsx"
```

**示例**：
```bash
# 假设您的 PDF 在 documents 文件夹
python tools\parse_pdf_quote.py "documents\供应商报价单.pdf"

# 输出会自动保存为：documents\供应商报价单_解析结果_20260322_170000.xlsx
```

---

## 🚀 快速测试

### 步骤 1：准备测试文件
将您的 PDF 报价单放到 `documents` 文件夹（需要先创建）

### 步骤 2：运行测试
```bash
cd C:\projects\chip-automation-workflow
python tools\parse_pdf_quote.py "documents\你的报价单.pdf"
```

### 步骤 3：查看结果
打开生成的 Excel 文件，检查提取的数据

---

## 📁 项目结构

```
chip-automation-workflow/
├── tools/                      # 工具脚本
│   ├── parse_pdf_quote.py     # ✅ PDF 解析器 (已完成)
│   ├── 1688_listing.py        # ⏳ 1688 上架工具 (待开发)
│   ├── crm_sync.py            # ⏳ CRM 同步工具 (待开发)
│   ├── distribution.py         # ⏳ 多平台分发工具 (待开发)
│   └── dashboard.py            # ⏳ 数据看板工具 (待开发)
├── documents/                  # 📁 PDF 文件存放处 (请创建)
├── output/                     # 📊 生成的 Excel/报告 (请创建)
├── install-deps.bat           # 依赖安装脚本
└── README.md                  # 本文档
```

---

## 🎯 待开发工具

| 工具 | 功能 | 优先级 |
|------|------|--------|
| 1688 上架工具 | 自动发布产品到 1688 | 🔴 高 |
| CRM 同步工具 | 客户信息管理与同步 | 🔴 高 |
| 多平台分发 | 一键分发到多个电商平台 | 🟡 中 |
| 数据看板 | 销售数据可视化分析 | 🟡 中 |

---

## 💡 下一步

请告诉我：
1. **您有 PDF 报价单可以测试吗？** - 我可以帮您调整解析逻辑
2. **您希望优先开发哪个工具？**
   - 1688 自动上架
   - CRM 客户管理
   - 多平台分发
   - 数据看板

---

## 🔧 常见问题

### Q: 运行提示"python 不是可识别的命令"
**A**: 使用完整路径运行：
```bash
C:\Users\59605\AppData\Local\Python\pythoncore-3.14-64\python.exe tools\parse_pdf_quote.py "your_file.pdf"
```

### Q: 提取的数据不准确
**A**: PDF 格式千差万别，请提供样本文件，我可以定制解析规则

### Q: 如何批量处理多个 PDF？
**A**: 我可以帮您写一个批量处理脚本，请稍后告诉我

---

**KR，请告诉我您的测试结果或下一步需求！** 💪
