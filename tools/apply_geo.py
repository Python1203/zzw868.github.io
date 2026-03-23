#!/usr/bin/env python3
"""
scripts/apply_geo.py
批量为所有 HTML 文件注入 GEO（生成式引擎优化）标记：
  - meta description / keywords / author / date
  - Open Graph tags
  - Schema.org JSON-LD (WebPage / SoftwareApplication / TechArticle)
  - <main role="main"> + <article> 包裹
  - <aside aria-hidden="true">
  - rel="alternate" 指向 ai-friendly 版本
  - 所有 target="_blank" 补 rel="noopener noreferrer"
"""
import re, os, sys
from datetime import date

BASE_URL   = "https://zzw868.github.io"
AUTHOR     = "zzw868"
AUTHOR_URL = "https://zzw868.github.io"
TODAY      = date.today().isoformat()

# ── 每个文件的 GEO 元数据配置 ────────────────────────────────────────────────
PAGE_META = {
    "index.html": None,  # 已有完整 GEO，跳过

    "详细集成示例（React多功能+热门插件）.html": None,  # 已完整处理，跳过

    "ai-chat.html": {
        "title":       "2025年如何搭建本地AI智能聊天助手？多服务集成完整教程",
        "description": "基于 React 与 WebSocket 构建的 AI 智能聊天助手演示，支持多 AI 服务集成（OpenAI、本地 Ollama 等），含完整前端代码与部署指南。",
        "keywords":    "AI聊天助手,本地AI,Ollama,OpenAI,React,WebSocket,多服务集成,2025",
        "schema_type": "TechArticle",
        "slug":        "ai-chat",
    },
    "crypto-dashboard.html": {
        "title":       "2025年加密货币实时交易仪表板：React + WebSocket 数据可视化完整示例",
        "description": "基于 React 与 WebSocket 实现的加密货币实时价格监控仪表板，支持 BTC/ETH 等主流币种行情展示、K线图与涨跌提醒，含完整源码。",
        "keywords":    "加密货币仪表板,比特币,以太坊,React,WebSocket,实时数据,数据可视化,2025",
        "schema_type": "SoftwareApplication",
        "slug":        "crypto-dashboard",
    },
    "tools-showcase.html": {
        "title":       "2025年React热门插件完整展示：从地图到图表的实战集成指南",
        "description": "React 生态热门插件实战展示，涵盖 Leaflet 地图、Recharts 图表、PrismJS 代码高亮等主流库的集成示例与最佳实践。",
        "keywords":    "React插件,Leaflet,Recharts,PrismJS,前端开发,组件集成,2025",
        "schema_type": "TechArticle",
        "slug":        "tools-showcase",
    },
    "test-stock-chart.html": {
        "title":       "2025年实时股票价格预测趋势图：React + Recharts 可视化实战",
        "description": "使用 React 与 Recharts 构建的实时股票价格预测趋势图，展示 LSTM 模型预测结果与历史走势对比，适合金融数据可视化学习参考。",
        "keywords":    "股票预测,Recharts,React,数据可视化,LSTM,金融图表,实时行情,2025",
        "schema_type": "TechArticle",
        "slug":        "test-stock-chart",
    },
    "components-hub.html": {
        "title":       "张良工作室前端组件导航中心：React UI 组件库完整索引 2025",
        "description": "张良信息咨询服务工作室前端组件导航中心，汇聚所有 React UI 组件、布局示例与交互演示，一站式查找所需前端组件。",
        "keywords":    "React组件库,UI组件,前端导航,张良工作室,组件索引,2025",
        "schema_type": "WebPage",
        "slug":        "components-hub",
    },
    "all-components-demo.html": {
        "title":       "张良工作室全组件演示：React UI 组件完整展示页 2025",
        "description": "张良信息咨询服务工作室所有前端 UI 组件的完整演示页，包含按钮、卡片、导航栏、弹窗、表单等常用组件的交互效果与代码示例。",
        "keywords":    "React组件演示,UI组件,前端开发,张良工作室,组件展示,2025",
        "schema_type": "WebPage",
        "slug":        "all-components-demo",
    },
    "react-counter-demo.html": {
        "title":       "React Counter 组件实战演示：useState Hook 入门教程 2025",
        "description": "React Counter 计数器组件完整演示，通过 useState Hook 实现状态管理，适合 React 初学者理解组件状态与事件处理机制。",
        "keywords":    "React,useState,Hook,计数器组件,前端教程,React入门,2025",
        "schema_type": "TechArticle",
        "slug":        "react-counter-demo",
    },
    "tailwind-card-component.html": {
        "title":       "Tailwind CSS 卡片组件实战：响应式 Card UI 设计完整示例 2025",
        "description": "使用 Tailwind CSS 构建的响应式卡片组件，包含悬停动效、暗色模式与多种布局变体，可直接复用于个人博客或产品展示页。",
        "keywords":    "Tailwind CSS,卡片组件,响应式设计,UI组件,暗色模式,前端开发,2025",
        "schema_type": "TechArticle",
        "slug":        "tailwind-card-component",
    },
    "3-column-layout.html": {
        "title":       "CSS Flexbox 三栏布局完整示例：响应式三列页面布局教程 2025",
        "description": "使用 CSS Flexbox 实现的三栏响应式布局示例，包含左侧边栏、主内容区与右侧边栏，适配移动端，含完整 HTML/CSS 源码。",
        "keywords":    "CSS Flexbox,三栏布局,响应式布局,前端布局,CSS教程,2025",
        "schema_type": "TechArticle",
        "slug":        "3-column-layout",
    },
    "grid-layout.html": {
        "title":       "CSS Grid 四列两行布局完整示例：网格布局实战教程 2025",
        "description": "使用 CSS Grid 实现的 4 列 2 行网格布局示例，展示 grid-template-columns/rows 核心用法，含响应式断点与完整源码。",
        "keywords":    "CSS Grid,网格布局,四列布局,响应式设计,前端教程,2025",
        "schema_type": "TechArticle",
        "slug":        "grid-layout",
    },
    "fade-in-animation.html": {
        "title":       "CSS Fade-In 淡入动画完整示例：纯 CSS 过渡动效实战教程 2025",
        "description": "使用纯 CSS @keyframes 与 animation 属性实现的淡入动画效果，包含多种触发方式（页面加载、滚动、悬停），含完整源码。",
        "keywords":    "CSS动画,淡入效果,fade-in,@keyframes,CSS过渡,前端动效,2025",
        "schema_type": "TechArticle",
        "slug":        "fade-in-animation",
    },
    "modern-button.html": {
        "title":       "现代 CSS 按钮设计：悬停动效与渐变样式完整示例 2025",
        "description": "使用 CSS 实现的现代风格按钮组件，包含渐变背景、悬停缩放、波纹点击效果与暗色模式支持，可直接复用于任何前端项目。",
        "keywords":    "CSS按钮,悬停动效,渐变按钮,UI设计,前端组件,2025",
        "schema_type": "TechArticle",
        "slug":        "modern-button",
    },
    "navbar.html": {
        "title":       "响应式导航栏完整示例：CSS + JavaScript 移动端汉堡菜单教程 2025",
        "description": "使用 HTML/CSS/JavaScript 构建的响应式导航栏，包含移动端汉堡菜单、下拉子菜单与滚动固定效果，含完整源码与实现思路。",
        "keywords":    "响应式导航栏,汉堡菜单,CSS导航,移动端适配,前端教程,2025",
        "schema_type": "TechArticle",
        "slug":        "navbar",
    },
    "modal-popup.html": {
        "title":       "JavaScript 弹窗组件完整示例：Modal Popup 实战教程 2025",
        "description": "使用原生 JavaScript 实现的模态弹窗组件，支持点击遮罩关闭、键盘 ESC 退出与动画过渡，无需任何框架依赖，含完整源码。",
        "keywords":    "Modal弹窗,JavaScript弹窗,模态框,前端组件,原生JS,2025",
        "schema_type": "TechArticle",
        "slug":        "modal-popup",
    },
    "contact-form.html": {
        "title":       "联系表单完整示例：HTML + CSS 响应式表单设计与验证教程 2025",
        "description": "张良信息咨询服务工作室联系表单，使用 HTML5 表单验证与 CSS 响应式布局构建，支持姓名、邮箱、留言提交，含完整源码。",
        "keywords":    "联系表单,HTML表单,表单验证,响应式表单,前端开发,2025",
        "schema_type": "ContactPage",
        "slug":        "contact-form",
    },
    "integration-complete.html": {
        "title":       "张良工作室组件整合完成报告：React 前端项目集成总结 2025",
        "description": "张良信息咨询服务工作室前端组件整合完成报告，记录所有 React 组件的集成状态、部署路径与使用说明，供团队参考。",
        "keywords":    "组件整合,React项目,前端部署,张良工作室,集成报告,2025",
        "schema_type": "WebPage",
        "slug":        "integration-complete",
    },
    "financial-ai-dashboard/index.html": {
        "title":       "金融AI实时预测仪表板：LSTM 模型 + React 可视化完整项目 2025",
        "description": "基于 LSTM 深度学习模型的金融 AI 实时预测仪表板，使用 React 与 WebSocket 展示股票/加密货币价格预测结果，含完整项目导航与部署指南。",
        "keywords":    "金融AI,LSTM预测,股票预测,React仪表板,WebSocket,深度学习,数据可视化,2025",
        "schema_type": "SoftwareApplication",
        "slug":        "financial-ai-dashboard",
    },
}


def build_geo_head(meta: dict, filename: str) -> str:
    slug      = meta["slug"]
    page_url  = f"{BASE_URL}/{slug}/"
    schema_t  = meta["schema_type"]

    # JSON-LD
    if schema_t == "SoftwareApplication":
        jsonld = f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "{meta['title']}",
    "description": "{meta['description']}",
    "applicationCategory": "WebApplication",
    "operatingSystem": "Web",
    "author": {{"@type": "Person", "name": "{AUTHOR}", "url": "{AUTHOR_URL}"}},
    "datePublished": "{TODAY}",
    "url": "{page_url}"
  }}
  </script>"""
    elif schema_t == "ContactPage":
        jsonld = f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "ContactPage",
    "name": "{meta['title']}",
    "description": "{meta['description']}",
    "url": "{page_url}",
    "author": {{"@type": "Person", "name": "{AUTHOR}", "url": "{AUTHOR_URL}"}}
  }}
  </script>"""
    elif schema_t == "WebPage":
        jsonld = f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "{meta['title']}",
    "description": "{meta['description']}",
    "url": "{page_url}",
    "author": {{"@type": "Person", "name": "{AUTHOR}", "url": "{AUTHOR_URL}"}},
    "datePublished": "{TODAY}"
  }}
  </script>"""
    else:  # TechArticle (default)
        jsonld = f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "TechArticle",
    "headline": "{meta['title']}",
    "description": "{meta['description']}",
    "keywords": "{meta['keywords']}",
    "datePublished": "{TODAY}",
    "dateModified": "{TODAY}",
    "author": {{"@type": "Person", "name": "{AUTHOR}", "url": "{AUTHOR_URL}"}},
    "publisher": {{"@type": "Person", "name": "{AUTHOR}", "url": "{AUTHOR_URL}"}},
    "mainEntityOfPage": {{"@type": "WebPage", "@id": "{page_url}"}}
  }}
  </script>"""

    return f"""  <meta name="author" content="{AUTHOR}" />
  <meta name="description" content="{meta['description']}" />
  <meta name="keywords" content="{meta['keywords']}" />
  <meta name="date" content="{TODAY}" />
  <meta property="og:title" content="{meta['title']}" />
  <meta property="og:description" content="{meta['description']}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{page_url}" />
  <link rel="canonical" href="{page_url}" />
  <link rel="alternate" type="text/html" href="{BASE_URL}/ai-friendly/" title="AI-Friendly Version" />
{jsonld}"""


def inject_geo(html: str, meta: dict, filename: str) -> str:
    # 1. 替换 <title> 为语义化标题
    html = re.sub(
        r"<title>.*?</title>",
        f"<title>{meta['title']}</title>",
        html, count=1, flags=re.S
    )

    # 2. 在 </head> 前注入 GEO head 块（避免重复注入）
    if 'name="description"' not in html and 'application/ld+json' not in html:
        geo_block = build_geo_head(meta, filename)
        html = html.replace("</head>", f"{geo_block}\n</head>", 1)

    # 3. <aside> 加 aria-hidden（若存在且未标注）
    html = re.sub(
        r'<aside(?![^>]*aria-hidden)([^>]*)>',
        r'<aside aria-hidden="true"\1>',
        html
    )

    # 4. <main> 加 role="main"（若存在且未标注）
    html = re.sub(
        r'<main(?![^>]*role)([^>]*)>',
        r'<main role="main"\1>',
        html
    )

    # 5. 所有 target="_blank" 补 rel="noopener noreferrer"
    def fix_blank(m):
        tag = m.group(0)
        if 'noopener' not in tag:
            tag = tag.replace('target="_blank"', 'target="_blank" rel="noopener noreferrer"')
        return tag
    html = re.sub(r'<a [^>]*target="_blank"[^>]*>', fix_blank, html)

    return html


def process_file(filepath: str, meta: dict):
    with open(filepath, encoding="utf-8") as f:
        original = f.read()

    result = inject_geo(original, meta, os.path.basename(filepath))

    if result != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"  ✓ GEO injected → {os.path.basename(filepath)}")
    else:
        print(f"  ─ No change    → {os.path.basename(filepath)}")


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Base dir: {base}\n")

    skipped = 0
    processed = 0

    for rel_path, meta in PAGE_META.items():
        filepath = os.path.join(base, rel_path)
        if not os.path.exists(filepath):
            print(f"  ! Not found    → {rel_path}")
            continue
        if meta is None:
            print(f"  ○ Skipped      → {rel_path}  (already optimised)")
            skipped += 1
            continue
        process_file(filepath, meta)
        processed += 1

    print(f"\nDone. {processed} files processed, {skipped} skipped.")


if __name__ == "__main__":
    main()
