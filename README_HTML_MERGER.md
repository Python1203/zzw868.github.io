# 📑 HTML 文件自动化去重合并工具

> 一键合并多个 HTML 文件，智能提取 Body 内容，自动添加唯一 ID 容器，防止样式污染，只保留一份公共 CSS/JS 框架。

[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-支持-brightgreen)](.github/workflows/html_merge.yml)
[![Python](https://img.shields.io/badge/Python-3.7+-blue)](merge_html.py)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🎯 核心功能

### ✨ 主要特性

- **🔍 智能提取** - 自动从每个 HTML 文件中提取 `<body>` 内容
- **🆔 唯一 ID 容器** - 为每个合并的内容块添加唯一的 ID，防止样式冲突
- **♻️ 资源去重** - 自动检测并只保留一份公共的 CSS 和 JS 文件
- **🎨 美观布局** - 自动生成带样式的美观页面，响应式设计
- **📊 来源标注** - 每个内容块都会显示来源文件名
- **🚀 一键运行** - 支持本地脚本和 GitHub Actions 自动化

### 📋 适用场景

1. **GitHub Pages 整合** - 将多个独立页面合并为一个导航页
2. **文档合集** - 合并所有文档页面为完整文档
3. **作品集展示** - 将项目页面合并为作品集总览
4. **仓库文件整理** - 整理和合并多个 HTML 文件

## 🚀 快速开始

### 方式一：一键运行（推荐）

```bash
./run-merge.sh
```

### 方式二：手动运行

```bash
# 1. 安装依赖
pip install beautifulsoup4

# 2. 准备 HTML 文件
mkdir my_pages
# 把你的 HTML 文件放到 my_pages/ 目录

# 3. 运行
python merge_html.py
```

## 📁 文件夹结构

```
你的项目/
├── my_pages/           ← 把所有 HTML 文件放这里
│   ├── page1.html
│   ├── page2.html
│   └── ...
├── merge_html.py       ← Python 合并脚本
├── run-merge.sh        ← 快速启动脚本
├── .github/workflows/
│   └── html_merge.yml  ← GitHub Actions 工作流
├── QUICKSTART_MERGE.md ← 快速开始指南
└── MERGE_HTML_GUIDE.md ← 完整使用文档
```

## 💡 使用示例

### 本地使用

```bash
# 运行快速启动脚本
./run-merge.sh

# 或直接用 Python 运行
python merge_html.py
```

### GitHub Actions 自动合并

推送到仓库后自动合并：

```yaml
# 已配置在 .github/workflows/html_merge.yml
# 每次 push 到 main/master 分支时自动合并
```

### 代码中使用

```python
from merge_html import HTMLMerger

merger = HTMLMerger(
    source_dir='pages',
    output_file='combined.html'
)
merger.run(title='我的网站')
```

## 🔧 工作原理

### 1. 扫描 HTML 文件
```
my_pages/
├── about.html
├── contact.html
└── products.html
```

### 2. 提取 Body 内容
```python
# 从每个文件中提取 <body>...</body> 之间的内容
<body>
    <h1>原标题</h1>
    <p>原内容</p>
</body>
```

### 3. 添加唯一 ID 容器
```python
# 包装后的内容
<div id="merged-section-0-about" class="merged-section" data-source-file="about.html">
    <h1>原标题</h1>
    <p>原内容</p>
</div>
```

### 4. 收集公共资源
```python
# 统计所有 HTML 文件中引用的 CSS 和 JS
# 如果出现次数超过一半，则视为公共资源

# 结果：style.css 被识别为公共资源
# 只在最终文件中保留一次
```

### 5. 生成最终 HTML
```html
<!DOCTYPE html>
<html>
<head>
    <!-- 只保留一份公共 CSS -->
    <link rel="stylesheet" href="style.css">
    
    <!-- 添加容器样式 -->
    <style>
        .merged-section {
            margin-bottom: 50px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <!-- 所有内容块按顺序排列 -->
    <div id="merged-section-0-about" class="merged-section">
        <!-- about.html 的内容 -->
    </div>
    
    <div id="merged-section-1-contact" class="merged-section">
        <!-- contact.html 的内容 -->
    </div>
    
    <!-- 只保留一份公共 JS -->
    <script src="app.js"></script>
</body>
</html>
```

## 📊 运行效果

```
============================================================
🚀 HTML 文件自动化去重合并工具
============================================================
📂 源目录：my_pages
📄 输出文件：merged.html
============================================================
📁 找到 5 个 HTML 文件:
   - about.html
   - contact.html
   - index.html
   - products.html
   - services.html

🔗 检测到 2 个公共 CSS 文件:
   - style.css
   - bootstrap.min.css

📜 检测到 1 个公共 JS 文件:
   - app.js

🔄 开始提取并合并内容...
✅ 已处理：about.html
✅ 已处理：contact.html
✅ 已处理：index.html
✅ 已处理：products.html
✅ 已处理：services.html

✨ 成功合并 5 个文件内容

✅ 合并完成！文件已保存至：merged.html
📊 文件大小：125.45 KB

============================================================
🎉 合并成功!
============================================================
```

## 📖 文档

- **[QUICKSTART_MERGE.md](QUICKSTART_MERGE.md)** - 30 秒快速开始指南
- **[MERGE_HTML_GUIDE.md](MERGE_HTML_GUIDE.md)** - 完整使用文档
- **[.github/workflows/html_merge.yml](.github/workflows/html_merge.yml)** - GitHub Actions 配置

## ⚙️ 配置选项

### 修改源目录和输出文件

编辑 `merge_html.py` 底部的 `main()` 函数：

```python
def main():
    SOURCE_DIR = "my_html_files"    # 改成你的目录
    OUTPUT_FILE = "all_pages.html"  # 改成你想要的文件名
    PAGE_TITLE = "我的页面合集"      # 改成你想要的标题
    
    merger = HTMLMerger(source_dir=SOURCE_DIR, output_file=OUTPUT_FILE)
    merger.run(title=PAGE_TITLE)
```

### 环境变量配置

```bash
export HTML_MERGE_SOURCE_DIR="my_pages"
export HTML_MERGE_OUTPUT_FILE="merged.html"
export HTML_MERGE_TITLE="合并的页面"
```

## ⚠️ 注意事项

### ✅ 推荐做法
- 所有 HTML 文件使用 UTF-8 编码
- 确保每个文件都有 `<body>` 标签
- 使用相对路径引用资源（CSS、图片等）

### ❌ 避免的做法
- 不要在 HTML 中使用绝对路径
- 避免不同文件使用相同的 ID 名称
- JavaScript 变量使用 `let`/`const` 声明，避免全局污染

## 🐛 故障排除

### 问题：找不到 HTML 文件
```bash
# 检查目录是否存在
ls -la my_pages/

# 确认有 HTML 文件
ls my_pages/*.html
```

### 问题：ImportError: No module named bs4
```bash
# 安装依赖
pip install beautifulsoup4
```

### 问题：中文乱码
```bash
# 确保文件是 UTF-8 编码
file -I my_pages/*.html
```

## 🛠️ 依赖

- Python 3.7+
- beautifulsoup4 >= 4.9.3

安装依赖：
```bash
pip install -r requirements_merge.txt
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📬 联系方式

如有问题或建议，请提 Issue。

---

**开始使用吧！** 🎉

只需一行命令：`./run-merge.sh` 或 `python merge_html.py`
