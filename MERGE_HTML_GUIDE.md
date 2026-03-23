# HTML 文件自动化去重合并工具

## 📋 功能特性

1. **智能提取 Body 内容** - 自动从每个 HTML 文件中提取 `<body>` 标签内的内容
2. **唯一 ID 容器** - 为每个合并的内容块添加唯一的 ID，防止样式冲突
3. **公共资源去重** - 自动检测并只保留一份公共的 CSS 和 JS 文件
4. **样式隔离** - 通过容器包装，避免不同页面的样式相互干扰
5. **来源标注** - 每个内容块都会显示来源文件名
6. **美观布局** - 自动生成带样式的美观页面

## 🛠️ 使用方法

### 方法一：直接运行（使用默认配置）

```bash
python merge_html.py
```

### 方法二：自定义配置

```bash
python -c "
from merge_html import HTMLMerger

# 自定义参数
merger = HTMLMerger(
    source_dir='my_pages',      # HTML 文件所在目录
    output_file='merged.html'   # 输出文件名
)
merger.run(title='我的合并页面')  # 设置页面标题
```

## 📁 文件夹结构

确保你的文件夹结构如下：

```
项目根目录/
├── my_pages/           # 存放所有要合并的 HTML 文件
│   ├── page1.html
│   ├── page2.html
│   └── page3.html
├── merge_html.py       # 合并脚本
└── merged.html         # 生成的合并文件（运行后生成）
```

## ⚙️ 配置选项

### 环境变量配置

创建 `.env` 文件或在运行时设置：

```bash
export HTML_MERGE_SOURCE_DIR="my_pages"
export HTML_MERGE_OUTPUT_FILE="merged.html"
export HTML_MERGE_TITLE="合并的页面"
```

### 代码中配置

修改 `merge_html.py` 底部的 `main()` 函数：

```python
def main():
    SOURCE_DIR = "my_pages"        # 修改为你的源目录
    OUTPUT_FILE = "merged.html"    # 修改为你想要的输出文件名
    PAGE_TITLE = "我的页面"        # 修改为页面标题
    
    merger = HTMLMerger(source_dir=SOURCE_DIR, output_file=OUTPUT_FILE)
    merger.run(title=PAGE_TITLE)
```

## 🔍 工作原理

### 1. 扫描 HTML 文件
```python
# 自动扫描指定目录下的所有 .html 文件
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

page1.html: <link rel="stylesheet" href="style.css">
page2.html: <link rel="stylesheet" href="style.css">
page3.html: <link rel="stylesheet" href="style.css">

# 结果：style.css 被识别为公共资源，只在最终文件中保留一次
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

## 📊 输出示例

运行脚本后，你会看到类似这样的输出：

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

## 🎨 生成的页面特性

1. **响应式布局** - 自动适配移动端和桌面端
2. **来源标注** - 每个内容块上方显示来源文件名
3. **视觉分隔** - 内容块之间有清晰的分隔线和间距
4. **统一样式** - 所有块使用统一的卡片样式
5. **SEO 友好** - 包含 meta 标签和语义化 HTML

## 🔧 高级用法

### 仅提取特定文件
```python
merger = HTMLMerger(source_dir='my_pages')
merger.html_files = [Path('page1.html'), Path('page2.html')]
merger.merge_all()
merger.generate_merged_html(title='精选页面')
```

### 自定义容器样式
修改 `generate_merged_html()` 方法中的 `custom_css`：

```python
custom_css = """
<style>
    .merged-section {
        margin-bottom: 30px;
        padding: 25px;
        border-left: 4px solid #4CAF50;
        background-color: #f9f9f9;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
"""
```

### 添加导航目录
在 `generate_merged_html()` 方法中添加：

```python
# 生成目录
toc = "<nav><ul>"
for i, file_path in enumerate(self.html_files):
    container_id = f"merged-section-{i}-{file_path.stem}"
    toc += f'<li><a href="#{container_id}">{file_path.stem}</a></li>'
toc += "</ul></nav>"

# 插入到 <main> 标签后
merged_body = toc + "\n\n" + merged_body
```

## ⚠️ 注意事项

1. **依赖库** - 需要安装 `beautifulsoup4`：
   ```bash
   pip install beautifulsoup4
   ```

2. **编码格式** - 所有 HTML 文件必须使用 UTF-8 编码

3. **HTML 结构** - 确保每个 HTML 文件都有完整的 `<body>` 标签

4. **相对路径** - 如果 HTML 中有相对路径的资源（图片、CSS 等），需要确保路径正确

5. **JavaScript 冲突** - 如果多个页面有相同的 JS 变量或函数名，可能会冲突，建议使用模块化方案

## 🐛 故障排除

### 问题 1：找不到 HTML 文件
**解决**：检查 `my_pages` 目录是否存在，确保路径正确

### 问题 2：提取的内容为空
**解决**：检查 HTML 文件是否有正确的 `<body>` 标签

### 问题 3：样式错乱
**解决**：检查公共 CSS 是否正确检测，可以手动指定：
```python
merger.common_css = {'style.css', 'bootstrap.css'}
```

### 问题 4：中文乱码
**解决**：确保所有 HTML 文件保存为 UTF-8 编码

## 📝 实际案例

### GitHub Pages 多页面合并
```bash
# 将所有独立页面合并为一个索引页面
mkdir pages_to_merge
mv *.html pages_to_merge/  # 除了 index.html
python merge_html.py
# 生成 merged.html，可以重命名为 index.html
```

### 文档整合
```bash
# 合并所有文档页面
mkdir docs
mv doc_*.html docs/
python merge_html.py
# 生成完整的文档页面
```

### 作品集展示
```bash
# 合并所有项目展示页面
mkdir projects
mv project_*.html projects/
python merge_html.py
# 生成作品集总览页面
```

## 🚀 在 GitHub Actions 中使用

创建 `.github/workflows/merge-html.yml`：

```yaml
name: Merge HTML Files

on:
  push:
    branches: [ main ]

jobs:
  merge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      
      - name: Install dependencies
        run: pip install beautifulsoup4
      
      - name: Merge HTML files
        run: python merge_html.py
      
      - name: Commit and push
        run: |
          git config --global user.name 'GitHub Actions'
          git config --global user.email 'actions@github.com'
          git add merged.html
          git commit -m 'Auto-merge HTML files' || echo "No changes to commit"
          git push
```

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

**创建时间**: 2026-03-19  
**版本**: 1.0.0
