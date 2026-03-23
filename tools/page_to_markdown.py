#!/usr/bin/env python3
"""
scripts/page_to_markdown.py
将指定 HTML 页面的 <article> 主内容转换为 AI 友好的 Markdown，
并生成 /ai-friendly/index.html 供 Jina Reader 等工具直接抓取。

用法:
  python3 scripts/page_to_markdown.py <source.html> <output_dir>
"""
import re
import sys
import json
import os
from html.parser import HTMLParser
from datetime import datetime, timezone


# ── 1. 极简 HTML→文本提取器（只读 <article> 内容）──────────────────────────
class ArticleExtractor(HTMLParser):
    SKIP = {"script", "style", "head", "nav", "footer"}
    BLOCK = {"p", "li", "dt", "dd", "blockquote", "div",
             "section", "details", "summary", "tr"}

    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self._in_article = False
        self._tag_stack = []
        self._lines = []
        self._cur = []

    def _flush(self):
        text = "".join(self._cur).strip()
        # collapse whitespace
        text = re.sub(r"\s+", " ", text)
        if text:
            self._lines.append(text)
        self._cur = []

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        if attrs_d.get("aria-hidden") == "true":
            self._skip_depth += 1
        if tag in self.SKIP:
            self._skip_depth += 1
        if tag == "article":
            self._in_article = True
        self._tag_stack.append(tag)
        if not self._in_article or self._skip_depth:
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._flush()
            self._cur.append("#" * int(tag[1]) + " ")
        elif tag == "li":
            self._flush()
            self._cur.append("- ")
        elif tag == "summary":
            self._flush()
            self._cur.append("### ")
        elif tag in ("strong", "b"):
            self._cur.append("**")
        elif tag == "code":
            self._cur.append("`")
        elif tag in self.BLOCK:
            self._flush()

    def handle_endtag(self, tag):
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
        if tag in self.SKIP or (tag == "aside" and self._skip_depth):
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if not self._in_article or self._skip_depth:
            return
        if tag in ("strong", "b"):
            self._cur.append("**")
        elif tag == "code":
            self._cur.append("`")
        elif tag in ("h1","h2","h3","h4","h5","h6","p","li","summary","dt","dd"):
            self._flush()
        elif tag == "article":
            self._flush()
            self._in_article = False

    def handle_data(self, data):
        if self._skip_depth or not self._in_article:
            return
        text = data.strip()
        if text:
            self._cur.append(text + " ")

    def get_markdown(self):
        out, prev = [], ""
        for line in self._lines:
            line = line.strip()
            if not line or line == prev:
                continue
            if line.startswith("#") and prev and not prev.startswith("#"):
                out.append("")
            out.append(line)
            prev = line
        return "\n".join(out)


# ── 2. 从 JSON-LD 提取元数据 ────────────────────────────────────────────────
def extract_meta(html):
    meta = {"title": "", "description": "", "author": "",
            "date": "", "keywords": "", "url": "https://zzw868.github.io"}
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    if m:
        meta["title"] = m.group(1).strip()
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            obj = json.loads(block)
            if obj.get("@type") in ("TechArticle", "Article", "BlogPosting"):
                meta["description"] = obj.get("description", meta["description"])
                meta["keywords"]    = obj.get("keywords",    meta["keywords"])
                meta["date"]        = obj.get("datePublished", meta["date"])
                author = obj.get("author", {})
                if isinstance(author, dict):
                    meta["author"] = author.get("name", meta["author"])
                page = obj.get("mainEntityOfPage", {})
                if isinstance(page, dict):
                    meta["url"] = page.get("@id", meta["url"]) or meta["url"]
        except Exception:
            pass
    return meta


# ── 3. 生成 YAML Front-matter ────────────────────────────────────────────────
def build_frontmatter(meta):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return (
        "---\n"
        f'title: "{meta["title"]}"\n'
        f'description: "{meta["description"]}"\n'
        f'author: "{meta["author"]}"\n'
        f'date: "{meta["date"] or now}"\n'
        f'keywords: "{meta["keywords"]}"\n'
        f'canonical_url: "{meta["url"]}"\n'
        f'ai_friendly: true\n'
        f'generated_at: "{now}"\n'
        "---"
    )


# ── 4. Markdown body → 极简 HTML（零外部依赖）────────────────────────────────
def md_to_html(md_body):
    parts = []
    for line in md_body.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(#{1,4}) (.+)", line)
        if m:
            lvl = len(m.group(1))
            parts.append(f"<h{lvl}>{m.group(2).strip()}</h{lvl}>")
        elif line.startswith("- "):
            parts.append(f"<li>{line[2:].strip()}</li>")
        else:
            # inline bold
            line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            parts.append(f"<p>{line}</p>")
    return "\n".join(parts)


def build_html(meta, md_body):
    body = md_to_html(md_body)
    kw = f'<meta name="keywords" content="{meta["keywords"]}" />' if meta["keywords"] else ""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{meta["title"]} [AI-Friendly]</title>
  <meta name="description" content="{meta["description"]}" />
  {kw}
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{meta["url"]}" />
  <style>
    body{{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;line-height:1.75;color:#111}}
    h1,h2,h3,h4{{margin-top:2rem;line-height:1.3}}
    p,li{{margin:.35rem 0}}
    ul{{padding-left:1.5rem}}
    .notice{{background:#eff6ff;border-left:4px solid #3b82f6;padding:.75rem 1rem;margin-bottom:1.5rem;font-size:.85rem;color:#1d4ed8}}
    .meta{{color:#555;font-size:.85rem;border-bottom:1px solid #e5e7eb;padding-bottom:1rem;margin-bottom:1.5rem}}
  </style>
</head>
<body>
  <div class="notice">
    📖 <strong>AI-Friendly Version</strong> — plain-text optimised for LLM ingestion &amp; Jina Reader.<br/>
    Original: <a href="{meta["url"]}">{meta["url"]}</a>
  </div>
  <div class="meta">
    <strong>Author:</strong> {meta["author"]} &nbsp;·&nbsp;
    <strong>Published:</strong> {meta["date"]} &nbsp;·&nbsp;
    <a href="{meta["url"]}">View original</a>
  </div>
  <article>
{body}
  </article>
</body>
</html>"""


# ── 5. 主流程 ────────────────────────────────────────────────────────────────
def main():
    src     = sys.argv[1] if len(sys.argv) > 1 else "详细集成示例（React多功能+热门插件）.html"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "ai-friendly"

    with open(src, encoding="utf-8") as f:
        html = f.read()

    meta     = extract_meta(html)
    extractor = ArticleExtractor()
    extractor.feed(html)
    md_body  = extractor.get_markdown()

    os.makedirs(out_dir, exist_ok=True)

    md_path = os.path.join(out_dir, "index.md")
    full_md = build_frontmatter(meta) + "\n\n" + md_body
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(full_md)
    print(f"✓ Markdown  → {md_path}  ({len(full_md):,} chars)")

    html_path = os.path.join(out_dir, "index.html")
    html_out  = build_html(meta, md_body)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"✓ HTML      → {html_path}  ({len(html_out):,} chars)")

    print(f"\n--- Markdown preview (first 600 chars) ---")
    print(full_md[:600])


if __name__ == "__main__":
    main()
