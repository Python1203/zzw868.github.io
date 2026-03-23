#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动注入 AI 聊天组件到部署目录
将 index.html 中的 AI 聊天组件注入到 .deploy_git/index.html
"""

import re
import shutil
from datetime import datetime
from pathlib import Path

# 配置
SOURCE_FILE = "index.html"
DEPLOY_FILE = ".deploy_git/index.html"
BACKUP_DIR = ".backups"

def extract_ai_chat_component(source_path):
    """从源文件中提取 AI 聊天组件"""
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找 <!-- AI 悬浮聊天按钮 --> 到 </body> 之间的内容
    pattern = r'(<!-- AI 悬浮聊天按钮 -->.*?</script>)\s*</body>'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError("未找到 AI 聊天组件代码")
    
    return match.group(1)

def inject_component(deploy_path, component_code):
    """将 AI 聊天组件注入到部署文件</body>标签之前"""
    with open(deploy_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已包含
    if 'aiFloatBtn' in content:
        print("⚠️  警告：部署文件已包含 AI 聊天组件")
        response = input("   是否要覆盖？(y/n): ")
        if response.lower() != 'y':
            print("操作已取消")
            return False
    
    # 在 </body> 前插入
    new_content = content.replace('</body>', f'{component_code}\n\n</body>')
    
    with open(deploy_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    print("=" * 60)
    print("🔧 AI 聊天组件自动注入工具")
    print("=" * 60)
    print()
    
    # 检查文件
    source_path = Path(SOURCE_FILE)
    deploy_path = Path(DEPLOY_FILE)
    
    if not source_path.exists():
        print(f"❌ 错误：源文件不存在：{SOURCE_FILE}")
        return 1
    
    if not deploy_path.exists():
        print(f"❌ 错误：部署文件不存在：{DEPLOY_FILE}")
        print("💡 提示：请先运行 hexo generate 和 hexo deploy")
        return 1
    
    # 创建备份目录
    backup_dir = Path(BACKUP_DIR)
    backup_dir.mkdir(exist_ok=True)
    
    # 备份部署文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"index.html.{timestamp}.bak"
    shutil.copy2(deploy_path, backup_file)
    print(f"✓ 已创建备份：{backup_file}")
    print()
    
    try:
        # 提取组件
        print("📋 提取 AI 聊天组件...")
        component = extract_ai_chat_component(source_path)
        print("✓ 成功提取 AI 聊天组件")
        print()
        
        # 注入组件
        print("🔧 正在注入 AI 聊天组件...")
        success = inject_component(deploy_path, component)
        
        if not success:
            return 1
        
        print("✓ AI 聊天组件已成功注入")
        print()
        
        # 验证结果
        with open(deploy_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        if 'aiFloatBtn' in new_content:
            print("✅ 验证通过：AI 聊天组件已正确注入")
            print()
            
            # 显示统计信息
            origin_size = backup_file.stat().st_size
            new_size = deploy_path.stat().st_size
            added_size = new_size - origin_size
            
            print("=" * 60)
            print("📊 注入完成统计")
            print("=" * 60)
            print(f"原始大小：{origin_size:,} bytes")
            print(f"新大小：{new_size:,} bytes")
            print(f"增加：+{added_size:,} bytes")
            print()
            
            print("💡 下一步操作:")
            print("   cd .deploy_git && git add index.html && git commit && git push origin main:gh-pages")
            print()
            
            print("🎉 所有操作完成!")
            return 0
        else:
            print("❌ 错误：注入失败，AI 聊天组件未找到")
            print("💡 正在恢复备份...")
            shutil.copy2(backup_file, deploy_path)
            print("✓ 已恢复到原始状态")
            return 1
            
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
        print("💡 正在恢复备份...")
        shutil.copy2(backup_file, deploy_path)
        print("✓ 已恢复到原始状态")
        return 1

if __name__ == "__main__":
    exit(main())
