#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 文件自动化去重合并脚本
功能：
1. 遍历所有 HTML 文件
2. 提取每个文件的 <body> 内容
3. 自动给它们加上唯一的 ID 容器，防止样式污染
4. 只保留一份公共的 CSS 框架
5. 生成合并后的 HTML 文件
6. 支持 Pandoc 等多种合并方案

使用方法：
python merge_html.py
"""

import os
import re
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup


class HTMLMerger:
    """HTML 文件合并器 - 支持多种合并方案"""
    
    def __init__(self, source_dir: str = "my_pages", output_file: str = "merged.html",
                 use_iframe: bool = False, generate_toc: bool = True,
                 use_pandoc: bool = False):
        """
        初始化合并器
        
        Args:
            source_dir: 源 HTML 文件目录
            output_file: 输出文件名
            use_iframe: 是否使用 iframe 模式（避免 JS 冲突）
            generate_toc: 是否生成 TOC 导航
            use_pandoc: 是否使用 Pandoc 方案（需要安装 Pandoc）
        """
        self.source_dir = Path(source_dir)
        self.output_file = Path(output_file)
        self.html_files = []
        self.common_css = set()  # 存储公共 CSS
        self.unique_css = {}  # 存储每个页面独有的 CSS
        self.all_js = []  # 所有 JS 脚本
        self.merged_contents = []  # 存储合并的内容
        self.toc_items = []  # 存储 TOC 项
        self.use_iframe = use_iframe  # iframe 模式
        self.generate_toc = generate_toc  # 生成 TOC
        self.use_pandoc = use_pandoc  # Pandoc 模式
        
    def find_html_files(self) -> list:
        """查找源目录中的所有 HTML 文件"""
        if not self.source_dir.exists():
            print(f"❌ 错误：目录 '{self.source_dir}' 不存在")
            return []
        
        html_files = list(self.source_dir.glob("*.html"))
        self.html_files = sorted(html_files, key=lambda x: x.name)
        
        print(f"📁 找到 {len(self.html_files)} 个 HTML 文件:")
        for file in self.html_files:
            print(f"   - {file.name}")
        
        return self.html_files
    
    def extract_body_content(self, file_path: Path) -> tuple:
        """
        提取 HTML 文件的 body 内容、CSS 和 JS
        
        Args:
            file_path: HTML 文件路径
            
        Returns:
            (body_content, head_content, css_links, js_scripts, title)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 提取 body 内容
            body = soup.find('body')
            body_content = str(body) if body else ""
            
            # 提取 head 内容（包含完整的 CSS 引用）
            head = soup.find('head')
            head_content = str(head) if head else ""
            
            # 提取页面标题
            title_tag = soup.find('title')
            page_title = title_tag.get_text().strip() if title_tag else file_path.stem
            
            # 提取 CSS 链接
            css_links = []
            for link in soup.find_all('link', rel='stylesheet'):
                if link.get('href'):
                    css_links.append(link.get('href'))
            
            # 提取 JS 脚本
            js_scripts = []
            for script in soup.find_all('script', src=True):
                if script.get('src'):
                    js_scripts.append(script.get('src'))
            
            return body_content, head_content, css_links, js_scripts, page_title
            
        except Exception as e:
            print(f"❌ 读取文件 {file_path.name} 时出错：{e}")
            return "", "", [], [], ""
    
    def collect_common_resources(self):
        """收集所有 HTML 文件的公共资源（CSS 和 JS），并识别独有资源"""
        all_css = []
        all_js = []
        first_page_head = None  # 第一个页面的完整 head
        
        for i, file_path in enumerate(self.html_files):
            _, head_content, css_links, js_scripts, _ = self.extract_body_content(file_path)
            all_css.extend(css_links)
            all_js.extend(js_scripts)
            
            # 保存第一个页面的完整 head（包含所有 CSS）
            if i == 0 and head_content:
                first_page_head = head_content
            
            # 记录每个页面的独有 CSS
            self.unique_css[file_path.name] = css_links
        
        # 统计出现频率最高的 CSS 和 JS（作为公共资源）
        from collections import Counter
        css_counter = Counter(all_css)
        js_counter = Counter(all_js)
        
        # 选择出现次数超过一半的作为公共资源
        threshold = len(self.html_files) // 2
        
        self.common_css = {css for css, count in css_counter.items() if count > threshold}
        self.all_js = list(set(all_js))  # 去重所有 JS
        self.first_page_head = first_page_head
        
        print(f"\n🔗 检测到 {len(self.common_css)} 个公共 CSS 文件:")
        for css in sorted(self.common_css):
            print(f"   - {css}")
        
        # 显示独有 CSS
        unique_css_count = sum(len(css_list) for css_list in self.unique_css.values()) - len(self.common_css)
        if unique_css_count > 0:
            print(f"\n🎨 检测到 {unique_css_count} 个独有 CSS 文件（按需加载）:")
            for file_name, css_list in self.unique_css.items():
                unique_css = [css for css in css_list if css not in self.common_css]
                if unique_css:
                    print(f"   {file_name}: {', '.join(unique_css)}")
        
        print(f"\n📜 检测到 {len(self.all_js)} 个 JS 文件（已去重）:")
        for js in sorted(self.all_js):
            print(f"   - {js}")
    
    def extract_unique_body(self, file_path: Path, index: int) -> str:
        """
        提取并包装 body 内容为唯一 ID 的容器（或使用 iframe）
        
        Args:
            file_path: HTML 文件路径
            index: 文件索引
            
        Returns:
            包装后的 HTML 内容
        """
        body_content, head_content, css_links, js_scripts, page_title = self.extract_body_content(file_path)
        
        if not body_content:
            return ""
        
        # 生成唯一 ID
        unique_id = f"merged-section-{index}"
        file_name = file_path.stem.replace(' ', '-').lower()
        container_id = f"{unique_id}-{file_name}"
        
        # 添加到 TOC
        self.toc_items.append({
            'id': container_id,
            'title': page_title,
            'file': file_path.name,
            'index': index
        })
        
        # 获取该页面独有的 CSS
        page_unique_css = [css for css in css_links if css not in self.common_css]
        
        if self.use_iframe:
            # iframe 模式：完全隔离 JS 和样式
            wrapped_content = f'''
<!-- 开始：{file_path.name} -->
<div id="{container_id}" class="merged-section" data-source-file="{file_path.name}">
    <iframe src="{file_path.name}.html" loading="lazy" style="width: 100%; height: 800px; border: none; overflow: hidden;"></iframe>
</div>
<!-- 结束：{file_path.name} -->
'''
        else:
            # 普通模式：直接嵌入内容
            
            # 移除原有的 body 标签，只保留内部内容
            body_match = re.search(r'<body[^>]*>(.*?)</body>', body_content, re.DOTALL | re.IGNORECASE)
            if body_match:
                inner_content = body_match.group(1)
            else:
                inner_content = body_content
            
            # 添加该页面独有的 CSS（条件加载）
            unique_css_html = ""
            if page_unique_css:
                unique_css_html = "\n".join([f'    <link rel="stylesheet" href="{css}" data-lazy-css>' for css in page_unique_css])
                unique_css_html = f"\n<!-- 独有 CSS -->\n<div style=\"display: none;\">{unique_css_html}</div>\n"
            
            # 包装为带唯一 ID 的容器
            wrapped_content = f'''
<!-- 开始：{file_path.name} -->
<div id="{container_id}" class="merged-section" data-source-file="{file_path.name}">
    {unique_css_html}
    {inner_content}
</div>
<!-- 结束：{file_path.name} -->
'''
        
        return wrapped_content
    
    def merge_all(self):
        """合并所有 HTML 文件"""
        print("\n🔄 开始提取并合并内容...")
        
        for i, file_path in enumerate(self.html_files):
            wrapped_content = self.extract_unique_body(file_path, i)
            if wrapped_content:
                self.merged_contents.append(wrapped_content)
                print(f"✅ 已处理：{file_path.name}")
        
        print(f"\n✨ 成功合并 {len(self.merged_contents)} 个文件内容")
        print(f"📍 已生成 {len(self.toc_items)} 个 TOC 导航项")
    
    def generate_toc_sidebar(self) -> str:
        """
        生成侧边栏 TOC 导航
        
        Returns:
            TOC 导航 HTML
        """
        if not self.generate_toc or not self.toc_items:
            return ""
        
        toc_html = '''
<aside class="toc-sidebar" id="toc-sidebar">
    <div class="toc-header">
        <h3>📑 目录</h3>
        <button class="toc-toggle" onclick="toggleTOC()">☰</button>
    </div>
    <nav class="toc-nav">
        <ul>
'''
        
        for item in self.toc_items:
            toc_html += f'''            <li class="toc-item">
                <a href="#{item['id']}" title="{item['file']}">
                    <span class="toc-number">{item['index'] + 1}.</span>
                    <span class="toc-title">{item['title']}</span>
                </a>
            </li>
'''
        
        toc_html += '''        </ul>
    </nav>
</aside>
'''
        
        return toc_html
    
    def generate_merged_html(self, title: str = "合并的页面"):
        """
        生成最终的合并 HTML 文件
        
        Args:
            title: 页面标题
        """
        # 构建 CSS 链接
        css_section = ""
        if self.common_css:
            css_section = "\n".join([
                f'    <link rel="stylesheet" href="{css}">'
                for css in sorted(self.common_css)
            ])
        
        # 构建 JS 脚本（放在 body 底部，已去重）
        js_section = ""
        if self.all_js:
            js_section = "\n".join([
                f'    <script src="{js}"></script>'
                for js in sorted(self.all_js)
            ])
        
        # 合并所有内容
        merged_body = "\n\n".join(self.merged_contents)
        
        # 生成 TOC 侧边栏
        toc_sidebar = self.generate_toc_sidebar()
        
        # 添加分隔线样式和 TOC 样式
        custom_css = """
        <style>
            /* 基础样式 */
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }
            
            /* 合并区块样式 */
            .merged-section {
                margin-bottom: 50px;
                padding: 20px;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #fafafa;
                scroll-margin-top: 20px;
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
            
            /* TOC 侧边栏样式 */
            .toc-sidebar {
                position: fixed;
                top: 20px;
                left: 20px;
                width: 250px;
                max-height: calc(100vh - 40px);
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                z-index: 1000;
                overflow: hidden;
                transition: transform 0.3s ease;
            }
            .toc-sidebar.collapsed {
                transform: translateX(-230px);
            }
            .toc-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .toc-header h3 {
                margin: 0;
                font-size: 16px;
            }
            .toc-toggle {
                background: none;
                border: none;
                color: white;
                font-size: 20px;
                cursor: pointer;
                padding: 5px;
                border-radius: 4px;
                transition: background 0.3s;
            }
            .toc-toggle:hover {
                background: rgba(255,255,255,0.2);
            }
            .toc-nav {
                overflow-y: auto;
                max-height: calc(100vh - 100px);
                padding: 10px 0;
            }
            .toc-nav ul {
                list-style: none;
                margin: 0;
                padding: 0;
            }
            .toc-item {
                margin: 0;
            }
            .toc-item a {
                display: block;
                padding: 8px 15px;
                color: #555;
                text-decoration: none;
                transition: all 0.2s;
                border-left: 3px solid transparent;
            }
            .toc-item a:hover {
                background: #f5f5f5;
                border-left-color: #667eea;
                color: #333;
            }
            .toc-number {
                display: inline-block;
                width: 25px;
                color: #999;
                font-size: 12px;
            }
            .toc-title {
                font-size: 14px;
            }
            
            /* 响应式设计 */
            @media (max-width: 768px) {
                .toc-sidebar {
                    left: 0;
                    right: 0;
                    bottom: 0;
                    top: auto;
                    width: 100%;
                    max-height: 300px;
                    border-radius: 0;
                    transform: translateY(270px);
                }
                .toc-sidebar.collapsed {
                    transform: translateY(0);
                }
                main {
                    padding-bottom: 320px;
                }
            }
            
            /* 懒加载 CSS 支持 */
            [data-lazy-css] {
                /* 标记为懒加载的 CSS */
            }
            
            /* iframe 容器优化 */
            .merged-section iframe {
                border-radius: 4px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        </style>
        
        <!-- TOC 交互脚本 -->
        <script>
        function toggleTOC() {
            const sidebar = document.getElementById('toc-sidebar');
            sidebar.classList.toggle('collapsed');
        }
        
        // 平滑滚动
        document.querySelectorAll('.toc-item a').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const target = document.getElementById(targetId);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
        
        // 懒加载 CSS（如果需要）
        document.addEventListener('DOMContentLoaded', function() {
            const lazyCSS = document.querySelectorAll('[data-lazy-css]');
            lazyCSS.forEach(link => {
                const href = link.getAttribute('href');
                if (href) {
                    const newLink = document.createElement('link');
                    newLink.rel = 'stylesheet';
                    newLink.href = href;
                    document.head.appendChild(newLink);
                }
            });
        });
        </script>
        """
        
        # 生成完整 HTML
        final_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="generator" content="HTML Merger Script v2.0">
    <meta name="created" content="{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}">
    
    <!-- 公共 CSS（只保留一份） -->
{css_section}
    
    <!-- 自定义样式和 TOC -->
{custom_css}
</head>
<body>
    <!-- TOC 侧边栏导航 -->
{toc_sidebar}
    
    <!-- 主内容区 -->
    <div class="main-content" style="margin-left: 290px; padding: 20px;">
        <header style="text-align: center; padding: 30px 0; margin-bottom: 40px;">
            <h1>{title}</h1>
            <p style="color: #666;">自动生成于 {datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
            <p style="color: #999; font-size: 14px;">共合并 {len(self.merged_contents)} 个 HTML 文件</p>
        </header>
        
        <main>
{merged_body}
        </main>
        
        <footer style="text-align: center; padding: 30px 0; margin-top: 50px; border-top: 2px solid #e0e0e0;">
            <p style="color: #999; font-size: 12px;">
                此页面由 HTML Merger Script v2.0 自动生成<br>
                生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </footer>
    </div>
    
    <!-- 所有 JS（已去重） -->
{js_section}
</body>
</html>
"""
        
        # 保存文件
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(final_html)
            
            print(f"\n✅ 合并完成！文件已保存至：{self.output_file}")
            print(f"📊 文件大小：{os.path.getsize(self.output_file) / 1024:.2f} KB")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 保存文件时出错：{e}")
            return False
    
    def run(self, title: str = "合并的页面"):
        """
        执行完整的合并流程
        
        Args:
            title: 最终页面的标题
        """
        print("=" * 60)
        print("🚀 HTML 文件自动化去重合并工具")
        print("=" * 60)
        print(f"📂 源目录：{self.source_dir}")
        print(f"📄 输出文件：{self.output_file}")
        print("=" * 60)
        
        # 1. 查找 HTML 文件
        if not self.find_html_files():
            return False
        
        # 2. 收集公共资源
        self.collect_common_resources()
        
        # 3. 合并所有内容
        self.merge_all()
        
        # 4. 生成最终文件
        success = self.generate_merged_html(title)
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 合并成功!")
        else:
            print("❌ 合并失败")
        print("=" * 60)
        
        return success


def main():
    """主函数"""
    # 配置参数
    SOURCE_DIR = "my_pages"  # 存放 HTML 文件的文件夹
    OUTPUT_FILE = "merged.html"  # 输出文件名
    PAGE_TITLE = "合并的页面"  # 页面标题
    
    # 高级选项
    USE_IFRAME = False  # 设置为 True 使用 iframe 模式（避免 JS 冲突）
    GENERATE_TOC = True  # 是否生成 TOC 导航
    
    # 创建合并器并运行
    merger = HTMLMerger(
        source_dir=SOURCE_DIR,
        output_file=OUTPUT_FILE,
        use_iframe=USE_IFRAME,
        generate_toc=GENERATE_TOC
    )
    merger.run(title=PAGE_TITLE)


if __name__ == "__main__":
    main()
