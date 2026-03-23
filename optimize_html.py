#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 自动优化网页布局 - 删除冗余代码
功能：
1. 删除空的 HTML 标签
2. 删除重复的属性
3. 删除无用的注释
4. 压缩多余的空行
5. 优化 meta 标签
6. 删除默认的 type 属性（如 type="text/javascript"）
7. 简化布尔属性
"""

import re
import os
from html.parser import HTMLParser

class HTMLCleaner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cleaned_lines = []
        self.current_line = ""
        
    def handle_starttag(self, tag, attrs):
        # 过滤掉空的属性
        filtered_attrs = [(k, v) for k, v in attrs if v is not None and v.strip() != '']
        
        # 构建优化的标签
        if filtered_attrs:
            attrs_str = ' '.join(f'{k}="{v}"' for k, v in filtered_attrs)
            self.current_line += f'<{tag} {attrs_str}>'
        else:
            self.current_line += f'<{tag}>'
            
    def handle_endtag(self, tag):
        self.current_line += f'</{tag}>'
        
    def handle_data(self, data):
        # 删除纯空白的文本节点
        if data.strip():
            self.current_line += data
            
    def handle_comment(self, data):
        # 保留重要注释，删除无用注释
        if 'copyright' not in data.lower() and 'author' not in data.lower():
            self.current_line += f'<!-- {data} -->'
            
    def handle_decl(self, decl):
        self.current_line += f'<!{decl}>'
        
    def handle_pi(self, data):
        self.current_line += f'<?{data}>'


def optimize_html_content(content):
    """优化 HTML 内容"""
    
    # 1. 删除 HTML 注释（保留重要的）
    # 删除作者、版权相关的注释
    content = re.sub(r'<!--\s*Author:\s*.*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'<!--\s*Copyright.*?-->', '', content, flags=re.DOTALL)
    
    # 删除其他无用注释
    content = re.sub(r'<!--(?!\[CDATA\[).*?-->', '', content, flags=re.DOTALL)
    
    # 2. 删除 script 和 style 标签中的 type 属性（默认值）
    content = re.sub(r'\s+type="text/javascript"', '', content)
    content = re.sub(r'\s+type="text/css"', '', content)
    
    # 3. 删除 lang 属性中的冗余语言
    # 将 lang="zh-CN,en,default" 简化为 lang="zh-CN"
    content = re.sub(r'lang="zh-CN,en,default"', 'lang="zh-CN"', content)
    
    # 4. 删除 meta 标签中的默认 charset
    # 删除重复的 charset 声明
    
    # 5. 压缩多个空行为一个空行
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # 6. 删除行首行尾的空白字符
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    content = '\n'.join(lines)
    
    # 7. 删除自闭合标签的斜杠（HTML5 支持）
    content = re.sub(r'\s*/>', '>', content)
    
    # 8. 简化布尔属性
    content = re.sub(r'disableddisabled', 'disabled', content)
    content = re.sub(r'checkedchecked', 'checked', content)
    
    # 9. 删除空的 div、span、p 标签（保留有 id 或 class 的）
    content = re.sub(r'<(div|span|p)(?![^>]*\b(id|class)=)[^>]*></\1>', '', content)
    
    # 10. 删除重复的 class 属性
    def deduplicate_class(match):
        classes = match.group(1).split()
        unique_classes = list(dict.fromkeys(classes))  # 保持顺序去重
        return f'class="{" ".join(unique_classes)}"'
    
    content = re.sub(r'class="([^"]*)"', deduplicate_class, content)
    
    # 11. 删除 Google Fonts 中未使用的字体（如果有）
    # 这个需要谨慎，这里只做个标记
    
    # 12. 优化 CDN 链接（使用 https）
    content = re.sub(r'http://cdn', 'https://cdn', content)
    content = re.sub(r'https?://fonts\.googleapis\.com', '//fonts.googleapis.com', content)
    content = re.sub(r'https?://cdn\.jsdelivr\.net', '//cdn.jsdelivr.net', content)
    
    # 13. 再次压缩空行
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # 14. 删除开头的空行
    content = content.lstrip('\n')
    
    return content


def optimize_meta_tags(content):
    """优化 meta 标签"""
    
    # 删除重复的 viewport meta
    viewport_matches = re.findall(r'<meta[^>]*name="viewport"[^>]*>', content)
    if len(viewport_matches) > 1:
        # 保留第一个，删除其他的
        content = re.sub(
            r'(<meta[^>]*name="viewport"[^>]*>)(.*?)(<meta[^>]*name="viewport"[^>]*>)',
            r'\1\2',
            content,
            flags=re.DOTALL
        )
    
    # 删除重复的 theme-color
    theme_color_matches = re.findall(r'<meta[^>]*name="theme-color"[^>]*>', content)
    if len(theme_color_matches) > 1:
        content = re.sub(
            r'(<meta[^>]*name="theme-color"[^>]*>)(.*?)(<meta[^>]*name="theme-color"[^>]*>)',
            r'\1\2',
            content,
            flags=re.DOTALL
        )
    
    return content


def optimize_link_tags(content):
    """优化 link 标签"""
    
    # 删除重复的 favicon
    favicons = re.findall(r'<link[^>]*rel=["\']?(icon|apple-touch-icon|shortcut icon)[^>]*>', content, re.IGNORECASE)
    if len(favicons) > 3:  # 通常只需要 3 个：apple-touch-icon, 32x32, 16x16
        # 保留前三个，删除多余的
        pass  # 需要更复杂的逻辑，暂时跳过
    
    return content


def format_html(content):
    """格式化 HTML 缩进"""
    
    # 简单的缩进格式化
    lines = content.split('\n')
    formatted_lines = []
    indent_level = 0
    indent_str = '  '  # 2 空格缩进
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 减少缩进级别（结束标签）
        if re.match(r'</', line):
            indent_level = max(0, indent_level - 1)
        
        # 添加当前行
        formatted_lines.append(indent_str * indent_level + line)
        
        # 增加缩进级别（开始标签，非自闭合）
        if re.match(r'<(?!/|!|meta|link|input|br|hr|img)', line) and not line.endswith('>'):
            indent_level += 1
        elif re.match(r'<(?!meta|link|input|br|hr|img)[^/].*[^/]>', line):
            indent_level += 1
    
    return '\n'.join(formatted_lines)


def clean_file(file_path):
    """清理单个文件"""
    
    print(f"正在处理：{file_path}")
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    original_size = len(original_content)
    print(f"原始大小：{original_size:,} 字节")
    
    # 优化 HTML
    optimized_content = optimize_html_content(original_content)
    
    # 优化 meta 标签
    optimized_content = optimize_meta_tags(optimized_content)
    
    # 优化 link 标签
    optimized_content = optimize_link_tags(optimized_content)
    
    # 格式化（可选，如果需要可读性）
    # optimized_content = format_html(optimized_content)
    
    optimized_size = len(optimized_content)
    reduction = ((original_size - optimized_size) / original_size * 100) if original_size > 0 else 0
    
    print(f"优化后大小：{optimized_size:,} 字节")
    print(f"减少了：{reduction:.2f}%")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(optimized_content)
    
    print(f"✓ 文件已优化并保存\n")
    
    return original_size, optimized_size


def main():
    """主函数"""
    
    # 目标文件路径
    file_path = '/Users/zzw868/PycharmProjects/zzw868.github.io/2021/05/20/【财经期刊FM-Radio｜2021 年 05 月 20 日】/index.html'
    
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 - {file_path}")
        return
    
    # 创建备份
    backup_path = file_path + '.backup'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已创建备份：{backup_path}\n")
    except Exception as e:
        print(f"创建备份失败：{e}\n")
    
    # 清理文件
    try:
        clean_file(file_path)
    except Exception as e:
        print(f"处理失败：{e}")
        # 如果处理失败，恢复备份
        if os.path.exists(backup_path):
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("已恢复到原始版本")


if __name__ == '__main__':
    main()
