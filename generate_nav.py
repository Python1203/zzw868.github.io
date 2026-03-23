#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成 HTML 导航页面
扫描指定目录中的 HTML 文件，生成带侧边栏导航的 index.html
"""

import os
import re
from pathlib import Path

def scan_html_files(directory='.', exclude_files=None):
    """
    扫描目录中的 HTML 文件
    
    Args:
        directory: 要扫描的目录
        exclude_files: 要排除的文件列表
        
    Returns:
        list: HTML 文件名列表（已排序）
    """
    if exclude_files is None:
        exclude_files = ['index.html', 'template.html']
    
    # 获取所有 HTML 文件
    files = [f for f in os.listdir(directory) 
             if f.endswith('.html') and f not in exclude_files]
    files.sort()
    
    return files

def generate_pages_config(files):
    """
    生成 JavaScript 页面配置
    
    Args:
        files: HTML 文件名列表
        
    Returns:
        str: JavaScript 数组格式的页面配置
    """
    lines = []
    for f in files:
        # 美化显示名称（去掉 .html 后缀，替换连字符为空格）
        name = f.replace('.html', '').replace('-', ' ').replace('_', ' ')
        # 首字母大写
        name = ' '.join(word.capitalize() for word in name.split())
        
        lines.append(f'        {{ name: "{name}", url: "{f}" }},')
    
    return '\n'.join(lines)

def generate_index_html(template_file='template.html', output_file='index.html', directory='.'):
    """
    根据模板生成最终的 index.html
    
    Args:
        template_file: 模板文件路径
        output_file: 输出文件路径
        directory: HTML 文件所在目录
    """
    # 扫描 HTML 文件
    print(f"📁 正在扫描目录：{directory}")
    files = scan_html_files(directory)
    
    if not files:
        print("⚠️  未找到任何 HTML 文件")
        pages_config = ""
    else:
        print(f"✅ 找到 {len(files)} 个 HTML 文件:")
        for f in files:
            print(f"   - {f}")
        pages_config = generate_pages_config(files)
    
    # 读取模板文件
    template_path = Path(template_file)
    if not template_path.exists():
        print(f"❌ 模板文件不存在：{template_file}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 替换占位符
    if '<!-- CONFIG_PLACEHOLDER -->' in template_content:
        # 如果有占位符，替换为实际配置
        final_content = template_content.replace(
            '<!-- CONFIG_PLACEHOLDER -->',
            pages_config if pages_config else '// 暂无文件'
        )
    else:
        # 如果没有占位符，尝试直接插入到 pages 数组中
        pattern = r'(const pages = \[)(.*?)(\];)'
        match = re.search(pattern, template_content, re.DOTALL)
        if match:
            final_content = template_content.replace(
                match.group(0),
                f'const pages = [\n{pages_config if pages_config else "// 暂无文件"}\n];'
            )
        else:
            print("⚠️  未找到 pages 数组或占位符，使用原始模板")
            final_content = template_content
    
    # 写入输出文件
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"\n✅ 成功生成：{output_file}")
    print(f"📊 包含 {len(files)} 个页面")
    
    return True

def main():
    """主函数"""
    import sys
    
    # 默认参数
    directory = '.'
    template_file = 'template.html'
    output_file = 'index.html'
    
    # 支持命令行参数
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    if len(sys.argv) > 2:
        template_file = sys.argv[2]
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    
    print("=" * 60)
    print("🔧 自动生成 HTML 导航页面")
    print("=" * 60)
    print(f"📂 扫描目录：{directory}")
    print(f"📄 模板文件：{template_file}")
    print(f"📤 输出文件：{output_file}")
    print("=" * 60)
    print()
    
    # 生成 index.html
    success = generate_index_html(template_file, output_file, directory)
    
    print()
    print("=" * 60)
    if success:
        print("🎉 生成成功!")
    else:
        print("❌ 生成失败")
    print("=" * 60)

if __name__ == "__main__":
    main()
