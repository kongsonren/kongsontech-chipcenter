# Python 环境安装指南 (Windows)

## 🎯 问题说明
您的系统 Python 环境被限制，无法直接安装依赖包。请按以下步骤解决。

---

## ✅ 方案 1：手动安装 Python (推荐)

### 步骤 1：下载 Python
1. 访问官网：https://www.python.org/downloads/
2. 下载 **Python 3.11.x** (推荐 3.11.9)
3. 运行安装程序

### 步骤 2：安装时配置
⚠️ **关键步骤**：在安装界面勾选：
- ✅ **Add Python to PATH** (添加到环境变量)
- ✅ **Install pip** (包管理器)

### 步骤 3：验证安装
打开**新的命令提示符窗口**，运行：
```bash
python --version
pip --version
```

### 步骤 4：安装项目依赖
```bash
cd C:\projects\chip-automation-workflow
pip install pdfplumber pandas openpyxl python-docx matplotlib plotly
```

---

## 🚀 方案 2：使用 Anaconda (更简单)

### 步骤 1：下载 Anaconda
- 官网：https://www.anaconda.com/download
- 下载 Windows 版本 (约 500MB)

### 步骤 2：安装
- 双击运行安装程序
- 按默认选项安装即可

### 步骤 3：使用
打开 **Anaconda Prompt**，运行：
```bash
conda create -n chip-automation python=3.11
conda activate chip-automation
pip install pdfplumber pandas openpyxl python-docx matplotlib plotly
```

---

## 💡 方案 3：临时测试 (无需安装)

如果只是想看效果，可以用在线环境测试：

### Google Colab
1. 访问：https://colab.research.google.com/
2. 新建 Notebook
3. 运行以下代码：
```python
# 安装依赖
!pip install pdfplumber pandas openpyxl python-docx matplotlib plotly

# 上传您的规格书 PDF
from google.colab import files
uploaded = files.upload()

# 运行解析器
import pdfplumber
# ... (复制 datasheet_parser.py 的代码)
```

---

## 📦 依赖包说明

| 包名 | 用途 | 大小 |
|------|------|------|
| pdfplumber | PDF 解析 | 2.3 MB |
| pandas | 数据处理 | 12 MB |
| openpyxl | Excel 操作 | 3.1 MB |
| python-docx | Word 文档 | 1.8 MB |
| matplotlib | 图表绘制 | 10 MB |
| plotly | 交互式图表 | 8.5 MB |

总大小约 **38 MB**，下载时间视网络情况而定。

---

## 🔧 常见问题

### Q1: 安装时提示权限错误？
**A**: 右键安装程序 → **以管理员身份运行**

### Q2: pip 仍然不可用？
**A**: 在命令提示符运行：
```bash
python -m ensurepip --upgrade
```

### Q3: 网络慢下载失败？
**A**: 使用国内镜像：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pdfplumber pandas openpyxl python-docx matplotlib plotly
```

---

## 📞 需要帮助？

安装完成后，运行以下命令测试：
```bash
cd C:\projects\chip-automation-workflow
python scripts/datasheet_parser.py --help
```

如果看到帮助信息，说明环境配置成功！🎉
