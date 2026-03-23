# 🚀 快速开始 - HTML 文件合并工具

## ⚡ 30 秒快速使用

### 方式一：一键运行（推荐）

```bash
./run-merge.sh
```

这个脚本会自动：
1. ✅ 检查 Python 环境
2. ✅ 安装依赖
3. ✅ 创建示例文件
4. ✅ 执行合并
5. ✅ 询问是否打开结果

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
├── merge_html.py       ← 合并脚本
├── run-merge.sh        ← 快速启动脚本
└── merged.html         ← 生成的文件
```

## 🎯 核心功能

### 1. 自动提取 Body 内容
```python
# 输入：完整的 HTML 文件
<html><head>...</head><body><h1>内容</h1></body></html>

# 输出：只保留 body 内的内容
<h1>内容</h1>
```

### 2. 添加唯一 ID 防止冲突
```html
<!-- 自动为每个内容块添加唯一 ID -->
<div id="merged-section-0-page1" class="merged-section">
    <!-- page1.html 的内容 -->
</div>

<div id="merged-section-1-page2" class="merged-section">
    <!-- page2.html 的内容 -->
</div>
```

### 3. 智能去重 CSS/JS
```python
# 如果 10 个文件中有 8 个都引用了 style.css
# 最终只在 <head> 中保留一个

<link rel="stylesheet" href="style.css">  # 只出现一次
```

## 📊 运行示例

```bash
$ ./run-merge.sh

🚀 HTML 文件合并工具
====================

✅ Python 版本：Python 3.9.7

📦 检查依赖...
✅ beautifulsoup4 已安装

📁 找到 5 个 HTML 文件:
   - about.html
   - contact.html
   - index.html
   - products.html
   - services.html

🔗 检测到 2 个公共 CSS 文件:
   - style.css
   - bootstrap.min.css

🔄 开始提取并合并内容...
✅ 已处理：about.html
✅ 已处理：contact.html
✅ 已处理：index.html
✅ 已处理：products.html
✅ 已处理：services.html

✨ 成功合并 5 个文件内容

✅ 合并完成！文件已保存至：merged.html
📊 文件大小：125.45 KB

是否现在用浏览器打开？(y/n)
```

## 🎨 生成效果预览

生成的 `merged.html` 包含：

```html
<!DOCTYPE html>
<html>
<head>
    <title>合并的页面</title>
    
    <!-- 只保留一份公共 CSS -->
    <link rel="stylesheet" href="style.css">
    
    <!-- 自动添加美化样式 -->
    <style>
        .merged-section {
            margin-bottom: 50px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #fafafa;
        }
    </style>
</head>
<body>
    <header>
        <h1>合并的页面</h1>
        <p>自动生成于 2026 年 03 月 19 日</p>
        <p>共合并 5 个 HTML 文件</p>
    </header>
    
    <main>
        <!-- 每个页面独立显示，带来源标注 -->
        <div id="merged-section-0-about" data-source-file="about.html">
            <!-- about.html 的内容 -->
        </div>
        
        <div id="merged-section-1-contact" data-source-file="contact.html">
            <!-- contact.html 的内容 -->
        </div>
        
        <!-- ... 更多页面 -->
    </main>
    
    <!-- 只保留一份公共 JS -->
    <script src="app.js"></script>
</body>
</html>
```

## 🔧 自定义配置

### 修改源目录和输出文件名

编辑 `merge_html.py` 底部的 `main()` 函数：

```python
def main():
    SOURCE_DIR = "my_html_files"    # 改成你的目录
    OUTPUT_FILE = "all_pages.html"  # 改成你想要的文件名
    PAGE_TITLE = "我的页面合集"      # 改成你想要的标题
    
    merger = HTMLMerger(source_dir=SOURCE_DIR, output_file=OUTPUT_FILE)
    merger.run(title=PAGE_TITLE)
```

### 在代码中使用

```python
from merge_html import HTMLMerger

# 创建合并器
merger = HTMLMerger(
    source_dir='pages',
    output_file='combined.html'
)

# 运行
merger.run(title='我的网站')
```

## 💡 常见使用场景

### 1. GitHub Pages 整合
```bash
# 将所有独立的 HTML 页面合并为一个导航页
mkdir pages_backup
mv *.html pages_backup/  # 备份除 index.html 外的文件
python merge_html.py
mv merged.html index.html
```

### 2. 文档合集
```bash
# 合并所有文档页面
mkdir docs_src
mv doc_*.html docs_src/
python merge_html.py
# 生成完整的文档页面
```

### 3. 作品集展示
```bash
# 将所有项目页面合并为作品集总览
mkdir projects
mv project_*.html projects/
python merge_html.py
mv merged.html portfolio.html
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

## 🐛 快速故障排除

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

## 📖 完整文档

详细使用说明请查看：[MERGE_HTML_GUIDE.md](MERGE_HTML_GUIDE.md)

## 🆘 获取帮助

遇到问题？检查以下几点：
1. ✅ Python 3 是否安装：`python3 --version`
2. ✅ 依赖是否安装：`pip list | grep beautifulsoup4`
3. ✅ 目录结构是否正确：`ls -la my_pages/`

---

**开始使用吧！** 🎉

只需一行命令：`./run-merge.sh`
