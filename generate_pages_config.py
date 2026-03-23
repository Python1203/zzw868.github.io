#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成页面列表配置
用于生成 const pages = [...] 格式的 JavaScript 数组
"""

import os
import sys

def generate_pages_config(directory='.', exclude_files=None, output_format='js'):
    """
    扫描目录中的 HTML 文件并生成配置
    
    Args:
        directory: 要扫描的目录
        exclude_files: 要排除的文件列表
        output_format: 输出格式 ('js', 'json', 'py')
    """
    if exclude_files is None:
        exclude_files = ['index.html']
    
    # 获取所有 HTML 文件
    files = [f for f in os.listdir(directory) 
             if f.endswith('.html') and f not in exclude_files]
    files.sort()
    
    print(f"📁 找到 {len(files)} 个 HTML 文件:\n")
    
    # JavaScript 格式输出
    if output_format == 'js':
        print('const pages = [')
        for f in files:
            print(f'  {{ name: "{f}", url: "{f}" }},')
        print('];')
    
    # JSON 格式输出
    elif output_format == 'json':
        import json
        pages = [{'name': f, 'url': f} for f in files]
        print(json.dumps(pages, indent=2))
    
    # Python 格式输出
    elif output_format == 'py':
        print('pages = [')
        for f in files:
            print(f'    {{"name": "{f}", "url": "{f}"}},')
        print(']')
    
    return files

def main():
    """主函数"""
    # 默认扫描当前目录
    directory = './my_pages'
    
    # 检查目录是否存在
    if not os.path.exists(directory):
        print(f"⚠️  目录 '{directory}' 不存在，使用当前目录")
        directory = '.'
    
    print("=" * 60)
    print("🔧 自动生成页面列表配置")
    print("=" * 60)
    print(f"📂 扫描目录：{directory}")
    print("=" * 60)
    print()
    
    # 生成配置
    files = generate_pages_config(directory, output_format='js')
    
    print()
    print("=" * 60)
    print(f"✅ 共找到 {len(files)} 个 HTML 文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
