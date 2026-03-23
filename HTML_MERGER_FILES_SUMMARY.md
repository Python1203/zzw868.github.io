# 📦 HTML 文件合并工具 - 项目文件清单

## ✅ 已创建的文件列表

### 核心文件

1. **`merge_html.py`** (321 行)
   - 🎯 主要的 Python 合并脚本
   - 📋 功能：扫描 HTML、提取 body、添加唯一 ID、去重 CSS/JS
   - 🔧 使用：`python merge_html.py`

2. **`run-merge.sh`** (104 行)
   - 🚀 快速启动脚本（Bash）
   - 📋 功能：检查环境、安装依赖、创建示例、运行合并
   - 🔧 使用：`./run-merge.sh`

3. **`requirements_merge.txt`** (3 行)
   - 📦 Python 依赖文件
   - 📋 内容：beautifulsoup4>=4.9.3

### 文档文件

4. **`README_HTML_MERGER.md`** (301 行)
   - 📖 项目主文档
   - 📋 包含：功能介绍、快速开始、使用示例、配置选项

5. **`QUICKSTART_MERGE.md`** (276 行)
   - 🚀 快速开始指南
   - 📋 包含：30 秒上手、常见问题、故障排除

6. **`MERGE_HTML_GUIDE.md`** (351 行)
   - 📚 完整使用文档
   - 📋 包含：详细用法、高级配置、实际案例、GitHub Actions 集成

7. **`HTML_MERGER_FILES_SUMMARY.md`** (本文件)
   - 📝 项目文件总结和导航

### GitHub Actions 工作流

8. **`.github/workflows/html_merge.yml`** (128 行)
   - ⚙️ GitHub Actions 自动化合并配置
   - 📋 功能：推送时自动合并、生成报告、上传制品

### 生成的文件（运行后）

9. **`merged.html`** (83 行) - 示例输出
   - 📄 合并后的 HTML 文件
   - 📋 包含：3 个示例页面的合并结果

10. **`my_pages/`** 目录
    - `page1.html` - 示例页面 1
    - `page2.html` - 示例页面 2
    - `page3.html` - 示例页面 3

---

## 📊 文件统计

```
总计：
- Python 脚本：1 个 (321 行)
- Bash 脚本：1 个 (104 行)
- Markdown 文档：4 个 (约 1229 行)
- GitHub Actions: 1 个 (128 行)
- 配置文件：1 个 (3 行)
- 示例 HTML: 3 个
- 总代码量：~1785 行
```

---

## 🎯 使用方式对比

### 方式一：一键运行（最简单）
```bash
./run-merge.sh
```
**适合场景**：第一次使用，需要自动检查环境和安装依赖

### 方式二：直接运行 Python 脚本
```bash
python merge_html.py
```
**适合场景**：已经安装好依赖，只需要执行合并

### 方式三：GitHub Actions 自动运行
```bash
# 推送到 GitHub 仓库后自动执行
git push origin main
```
**适合场景**：CI/CD 自动化，每次推送自动合并

### 方式四：在代码中调用
```python
from merge_html import HTMLMerger

merger = HTMLMerger(source_dir='pages', output_file='all.html')
merger.run(title='我的页面')
```
**适合场景**：集成到其他 Python 项目中

---

## 📁 完整的文件夹结构

```
你的项目/
├── .github/
│   └── workflows/
│       └── html_merge.yml          ← GitHub Actions 配置
│
├── my_pages/                        ← 存放要合并的 HTML 文件
│   ├── page1.html                  ← 示例文件 1
│   ├── page2.html                  ← 示例文件 2
│   └── page3.html                  ← 示例文件 3
│
├── merge_html.py                    ← 核心 Python 脚本 ⭐
├── run-merge.sh                     ← 快速启动脚本
├── requirements_merge.txt           ← Python 依赖
│
├── README_HTML_MERGER.md            ← 项目主文档 📖
├── QUICKSTART_MERGE.md              ← 快速开始指南 🚀
├── MERGE_HTML_GUIDE.md              ← 完整使用文档 📚
├── HTML_MERGER_FILES_SUMMARY.md     ← 本文件（文件清单）
│
└── merged.html                      ← 生成的合并文件（运行后产生）
```

---

## 🔍 核心功能演示

### 1. 智能提取 Body 内容

**输入文件 (page1.html):**
```html
<!DOCTYPE html>
<html>
<head>
    <title>页面 1</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>这是页面 1</h1>
    <p>这是第一个示例页面的内容。</p>
</body>
</html>
```

**提取结果:**
```html
<h1>这是页面 1</h1>
<p>这是第一个示例页面的内容。</p>
```

### 2. 添加唯一 ID 容器

**包装后:**
```html
<div id="merged-section-0-page1" class="merged-section" data-source-file="page1.html">
    <h1>这是页面 1</h1>
    <p>这是第一个示例页面的内容。</p>
</div>
```

### 3. 智能去重 CSS/JS

**检测到多个文件都引用相同的资源:**
- page1.html → style.css
- page2.html → style.css
- page3.html → style.css

**最终只在合并文件中保留一次:**
```html
<head>
    <link rel="stylesheet" href="style.css">
    <!-- 只出现一次 -->
</head>
```

### 4. 自动生成美观页面

**最终输出 (merged.html):**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>合并的页面</title>
    
    <!-- 公共 CSS（只保留一份） -->
    <link rel="stylesheet" href="style.css">
    
    <!-- 自动添加的美化样式 -->
    <style>
        .merged-section {
            margin-bottom: 50px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #fafafa;
        }
        .merged-section[data-source-file]::before {
            content: "来源：" attr(data-source-file);
            display: block;
            font-size: 12px;
            color: #666;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px dashed #ccc;
        }
    </style>
</head>
<body>
    <header style="text-align: center; padding: 30px 0;">
        <h1>合并的页面</h1>
        <p style="color: #666;">自动生成于 2026 年 03 月 19 日 14:47</p>
        <p style="color: #999; font-size: 14px;">共合并 3 个 HTML 文件</p>
    </header>
    
    <main style="max-width: 1200px; margin: 0 auto; padding: 20px;">
        <!-- 页面 1 -->
        <div id="merged-section-0-page1" class="merged-section" data-source-file="page1.html">
            <h1>这是页面 1</h1>
            <p>这是第一个示例页面的内容。</p>
        </div>
        
        <!-- 页面 2 -->
        <div id="merged-section-1-page2" class="merged-section" data-source-file="page2.html">
            <h1>这是页面 2</h1>
            <p>这是第二个示例页面的内容。</p>
        </div>
        
        <!-- 页面 3 -->
        <div id="merged-section-2-page3" class="merged-section" data-source-file="page3.html">
            <h1>这是页面 3</h1>
            <p>这是第三个示例页面的内容。</p>
        </div>
    </main>
    
    <footer>
        <p>此页面由 HTML Merger Script 自动生成</p>
    </footer>
</body>
</html>
```

---

## 🎓 学习路径

### 初学者路线
1. 阅读 `QUICKSTART_MERGE.md` - 30 秒快速上手
2. 运行 `./run-merge.sh` - 体验一键合并
3. 查看生成的 `merged.html` - 了解输出效果
4. 阅读 `README_HTML_MERGER.md` - 了解更多功能

### 进阶使用者
1. 阅读 `MERGE_HTML_GUIDE.md` - 详细配置和高级用法
2. 修改 `merge_html.py` - 自定义合并逻辑
3. 配置 `.github/workflows/html_merge.yml` - 自动化流程
4. 集成到自己的项目中

---

## 💡 实际应用场景

### 场景 1: GitHub Pages 整合
```bash
# 将所有独立页面合并为一个导航页
mkdir pages_backup
mv *.html pages_backup/  # 备份除 index.html 外的文件
python merge_html.py
mv merged.html index.html
```

### 场景 2: 文档合集
```bash
# 合并所有文档页面
mkdir docs_src
mv doc_*.html docs_src/
python merge_html.py
# 生成完整的文档页面
```

### 场景 3: 作品集展示
```bash
# 将所有项目页面合并为作品集总览
mkdir projects
mv project_*.html projects/
python merge_html.py
mv merged.html portfolio.html
```

### 场景 4: GitHub Actions 自动化
```yaml
# 配置在 .github/workflows/html_merge.yml
# 每次 push 自动合并 HTML 文件
```

---

## ⚙️ 配置选项速查

### 修改源目录
```python
# 在 merge_html.py 的 main() 函数中
SOURCE_DIR = "my_html_files"  # 改成你的目录
```

### 修改输出文件名
```python
OUTPUT_FILE = "all_pages.html"  # 改成你想要的文件名
```

### 修改页面标题
```python
PAGE_TITLE = "我的页面合集"  # 改成你想要的标题
```

### 环境变量配置
```bash
export HTML_MERGE_SOURCE_DIR="my_pages"
export HTML_MERGE_OUTPUT_FILE="merged.html"
export HTML_MERGE_TITLE="合并的页面"
```

---

## 🐛 常见问题速查

### 问题 1: 找不到 HTML 文件
```bash
# 检查目录
ls -la my_pages/
```

### 问题 2: ImportError: No module named bs4
```bash
# 安装依赖
pip install beautifulsoup4
```

### 问题 3: 中文乱码
```bash
# 确保 UTF-8 编码
file -I my_pages/*.html
```

### 问题 4: 样式错乱
```python
# 手动指定公共 CSS
merger.common_css = {'style.css', 'bootstrap.css'}
```

---

## 📞 获取帮助

1. **快速问题** - 查看 `QUICKSTART_MERGE.md` 的故障排除部分
2. **详细文档** - 查看 `MERGE_HTML_GUIDE.md`
3. **项目总览** - 查看 `README_HTML_MERGER.md`
4. **提交 Issue** - 在 GitHub 仓库提 Issue

---

## 🎉 开始使用

**最简单的开始方式:**
```bash
./run-merge.sh
```

**查看生成的文件:**
```bash
open merged.html  # macOS
xdg-open merged.html  # Linux
start merged.html  # Windows
```

---

**祝你使用愉快！** 🚀

如有任何问题，请查阅相关文档或提 Issue。
