#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 自动优化网页布局 - 删除冗余代码
直接处理文件，不需要终端
"""

import os
import re

def optimize_html_file():
    """优化 HTML 文件"""
    
    file_path = '/Users/zzw868/PycharmProjects/zzw868.github.io/2021/05/20/【财经期刊FM-Radio｜2021 年 05 月 20 日】/index.html'
    backup_path = file_path + '.backup'
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 - {file_path}")
        return False
    
    print(f"正在处理：{file_path}")
    
    # 读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件失败：{e}")
        return False
    
    original_size = len(content)
    print(f"原始大小：{original_size:,} 字节")
    
    # 创建备份
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已创建备份：{backup_path}\n")
    except Exception as e:
        print(f"创建备份失败：{e}\n")
    
    # === 开始优化 ===
    
    # 1. 简化 lang 属性
    content = re.sub(r'lang="zh-CN,en,default"', 'lang="zh-CN"', content)
    print("✓ 简化 lang 属性")
    
    # 2. 删除 generator meta 标签
    content = re.sub(r'\s*<meta name="generator"[^>]*>\n?', '', content)
    print("✓ 删除 generator meta 标签")
    
    # 3. 删除 link 标签中的 type="image/png"
    content = re.sub(r'type="image/png"\s*', '', content)
    print("✓ 删除 favicon 的 type 属性")
    
    # 4. 删除 script 和 style 标签中的默认 type 属性
    content = re.sub(r'\s+type="text/javascript"', '', content)
    content = re.sub(r'\s+type="text/css"', '', content)
    print("✓ 删除默认的 type 属性")
    
    # 5. 删除空的 meta 标签
    content = re.sub(r'<meta[^>]*content=""[^>]*>\n?', '', content)
    print("✓ 删除空的 meta 标签")
    
    # 6. 压缩多个连续空行为一个空行
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    print("✓ 压缩空行")
    
    # 7. 删除行尾空格
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    content = '\n'.join(lines)
    print("✓ 删除行尾空格")
    
    # 8. 删除 HTML 注释（保留重要的）
    # 删除作者、版权相关的注释
    content = re.sub(r'<!--\s*Author:\s*.*?-->', '', content, flags=re.DOTALL)
    content = re.sub(r'<!--\s*Copyright.*?-->', '', content, flags=re.DOTALL)
    # 删除其他普通注释
    content = re.sub(r'<!--(?!\[CDATA\[).*?-->', '', content, flags=re.DOTALL)
    print("✓ 删除无用注释")
    
    # 9. 删除自闭合标签末尾的斜杠（HTML5 支持）
    content = re.sub(r'\s*/>', '>', content)
    print("✓ 简化自闭合标签")
    
    # 10. 优化 CDN 链接为协议相对 URL
    content = re.sub(r'https://cdn\.jsdelivr\.net', '//cdn.jsdelivr.net', content)
    content = re.sub(r'https://fonts\.googleapis\.com', '//fonts.googleapis.com', content)
    print("✓ 优化 CDN 链接")
    
    # 11. 删除重复的 class 属性值
    def deduplicate_class(match):
        classes = match.group(1).split()
        unique_classes = list(dict.fromkeys(classes))  # 保持顺序去重
        return f'class="{" ".join(unique_classes)}"'
    
    content = re.sub(r'class="([^"]*)"', deduplicate_class, content)
    print("✓ 删除重复的 class 值")
    
    # 12. 简化布尔属性
    content = re.sub(r'disableddisabled', 'disabled', content)
    content = re.sub(r'checkedchecked', 'checked', content)
    content = re.sub(r'selectedselected', 'selected', content)
    print("✓ 简化布尔属性")
    
    # 13. 再次压缩空行和空白
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()
    print("✓ 最终清理")
    
    # === 优化完成 ===
    
    optimized_size = len(content)
    reduction = ((original_size - optimized_size) / original_size * 100) if original_size > 0 else 0
    
    print(f"\n优化后大小：{optimized_size:,} 字节")
    print(f"减少了：{reduction:.2f}%")
    print(f"节省了：{(original_size - optimized_size):,} 字节")
    
    # 写回文件
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✓ 文件已优化并保存")
    except Exception as e:
        print(f"\n写入文件失败：{e}")
        # 如果失败，恢复备份
        if os.path.exists(backup_path):
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("已恢复到原始版本")
        return False
    
    return True


if __name__ == '__main__':
    success = optimize_html_file()
    if success:
        print("\n🎉 优化完成！")
    else:
        print("\n❌ 优化失败")
