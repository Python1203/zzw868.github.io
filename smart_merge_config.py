#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 驱动的配置智能合并与优化工具
用于 Next 主题配置的自动合并、优化和验证
"""

import yaml
import os
import sys
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


class ConfigMerger:
    """配置智能合并器"""
    
    def __init__(self, old_config_path: str, new_config_path: str, output_path: str):
        self.old_config_path = old_config_path
        self.new_config_path = new_config_path
        self.output_path = output_path
        self.old_config = {}
        self.new_config = {}
        self.merged_config = {}
        self.changes = []
        
    def load_configs(self) -> bool:
        """加载配置文件"""
        try:
            # 加载旧配置（用户自定义）
            if os.path.exists(self.old_config_path):
                with open(self.old_config_path, 'r', encoding='utf-8') as f:
                    self.old_config = yaml.safe_load(f) or {}
                print(f"✓ 已加载旧配置：{self.old_config_path}")
            else:
                print(f"⚠ 旧配置不存在：{self.old_config_path}")
            
            # 加载新配置（主题默认）
            if os.path.exists(self.new_config_path):
                with open(self.new_config_path, 'r', encoding='utf-8') as f:
                    self.new_config = yaml.safe_load(f) or {}
                print(f"✓ 已加载新配置：{self.new_config_path}")
            else:
                print(f"⚠ 新配置不存在：{self.new_config_path}")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ 加载配置失败：{str(e)}")
            return False
    
    def deep_merge(self, base: Dict, override: Dict, path: str = "") -> Dict:
        """
        深度合并两个字典
        策略：
        1. 保留用户自定义的值
        2. 添加新版本中的配置项
        3. 记录所有变更
        """
        result = base.copy()
        
        for key, value in override.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in result:
                # 新配置中的新键，直接添加
                result[key] = value
                self.changes.append({
                    'type': 'add',
                    'path': current_path,
                    'value': value,
                    'description': f'添加新配置项：{current_path}'
                })
            elif isinstance(value, dict) and isinstance(result.get(key), dict):
                # 都是字典，递归合并
                result[key] = self.deep_merge(result[key], value, current_path)
            else:
                # 保留旧值（用户自定义）
                if result[key] != value:
                    self.changes.append({
                        'type': 'keep',
                        'path': current_path,
                        'old_value': result[key],
                        'new_value': value,
                        'description': f'保留用户自定义：{current_path} = {result[key]}'
                    })
        
        return result
    
    def merge(self) -> Dict:
        """执行合并"""
        print("\n🔧 开始合并配置...")
        self.merged_config = self.deep_merge(self.old_config, self.new_config)
        print(f"✓ 合并完成，共 {len(self.changes)} 处变更\n")
        return self.merged_config
    
    def save_merged(self) -> bool:
        """保存合并后的配置"""
        try:
            # 创建备份目录
            backup_dir = ".theme_backups/config_merges"
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成带时间戳的备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"merged_config_{timestamp}.yml")
            
            # 保存合并后的配置
            with open(self.output_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self.merged_config,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                    width=120
                )
            
            # 同时保存到备份目录
            shutil.copy2(self.output_path, backup_file)
            
            print(f"✓ 已保存合并配置：{self.output_path}")
            print(f"✓ 备份文件：{backup_file}")
            return True
            
        except Exception as e:
            print(f"✗ 保存失败：{str(e)}")
            return False
    
    def generate_report(self, report_path: str) -> bool:
        """生成合并报告"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            report = f"""# 配置合并报告

## 📅 基本信息

- **生成时间**: {timestamp}
- **旧配置**: {self.old_config_path}
- **新配置**: {self.new_config_path}
- **输出文件**: {self.output_path}

## 📊 统计信息

- **总变更数**: {len(self.changes)}
- **新增配置项**: {sum(1 for c in self.changes if c['type'] == 'add')}
- **保留自定义**: {sum(1 for c in self.changes if c['type'] == 'keep')}

## 📝 变更详情

"""
            
            # 按类型分组显示
            adds = [c for c in self.changes if c['type'] == 'add']
            keeps = [c for c in self.changes if c['type'] == 'keep']
            
            if adds:
                report += "### ➕ 新增配置项\n\n"
                for change in adds:
                    report += f"- `{change['path']}`\n"
                report += "\n"
            
            if keeps:
                report += "### 🔒 保留的用户自定义\n\n"
                for change in keeps:
                    report += f"- `{change['path']}` = `{change['old_value']}`\n"
                report += "\n"
            
            report += """## 💡 建议

1. **检查配置**: 仔细查看合并后的配置文件
2. **测试网站**: 运行 `hexo clean && hexo g` 测试
3. **对比差异**: 使用 diff 工具对比变更
4. **提交备份**: 将备份提交到 Git

---
*此报告由 AI 配置合并工具自动生成*
"""
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"✓ 报告已生成：{report_path}")
            return True
            
        except Exception as e:
            print(f"✗ 生成报告失败：{str(e)}")
            return False
    
    def print_summary(self):
        """打印合并摘要"""
        print("\n" + "=" * 60)
        print("📋 合并摘要")
        print("=" * 60)
        
        if not self.changes:
            print("没有变更")
            return
        
        # 分组统计
        adds = sum(1 for c in self.changes if c['type'] == 'add')
        keeps = sum(1 for c in self.changes if c['type'] == 'keep')
        
        print(f"新增配置项：{adds}")
        print(f"保留自定义：{keeps}")
        
        print("\n详细变更:")
        for i, change in enumerate(self.changes[:20], 1):  # 只显示前 20 个
            if change['type'] == 'add':
                print(f"  {i}. ➕ {change['path']}")
            elif change['type'] == 'keep':
                print(f"  {i}. 🔒 {change['path']} = {change['old_value']}")
        
        if len(self.changes) > 20:
            print(f"  ... 还有 {len(self.changes) - 20} 个变更")
        
        print("=" * 60 + "\n")


class ConfigOptimizer:
    """配置优化器"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = {}
        self.optimizations = []
        
    def load_config(self) -> bool:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            print(f"✓ 已加载配置：{self.config_path}")
            return True
        except Exception as e:
            print(f"✗ 加载失败：{str(e)}")
            return False
    
    def optimize(self) -> Dict:
        """
        优化配置
        策略：
        1. 移除注释掉的无用配置
        2. 整理格式
        3. 添加推荐配置
        """
        print("\n🎯 开始优化配置...")
        
        # 示例优化：确保必要的配置存在
        necessary_configs = {
            'cache': {'enable': True},
            'minify': False,
            'darkmode': True,
        }
        
        for key, value in necessary_configs.items():
            if key not in self.config:
                self.config[key] = value
                self.optimizations.append({
                    'type': 'add',
                    'key': key,
                    'value': value,
                    'reason': '推荐的必要配置'
                })
        
        print(f"✓ 优化完成，共 {len(self.optimizations)} 处优化\n")
        return self.config
    
    def save_optimized(self, output_path: Optional[str] = None) -> bool:
        """保存优化后的配置"""
        target_path = output_path or self.config_path
        
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self.config,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                    width=120
                )
            
            print(f"✓ 已保存优化配置：{target_path}")
            return True
        except Exception as e:
            print(f"✗ 保存失败：{str(e)}")
            return False


def validate_config(config_path: str) -> Tuple[bool, List[str]]:
    """
    验证配置文件
    返回：(是否有效，错误列表)
    """
    errors = []
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not isinstance(config, dict):
            errors.append("配置文件格式错误：应该是字典类型")
            return False, errors
        
        # 检查常见错误
        if 'scheme' in config and config['scheme'] not in ['Muse', 'Mist', 'Pisces', 'Gemini']:
            errors.append(f"无效的 scheme: {config['scheme']}")
        
        if 'menu' in config and not isinstance(config['menu'], dict):
            errors.append("menu 应该是字典类型")
        
        return len(errors) == 0, errors
        
    except yaml.YAMLError as e:
        errors.append(f"YAML 解析错误：{str(e)}")
        return False, errors
    except Exception as e:
        errors.append(f"读取错误：{str(e)}")
        return False, errors


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI 配置智能合并与优化工具')
    parser.add_argument('action', choices=['merge', 'optimize', 'validate'],
                       help='操作类型')
    parser.add_argument('--old', '-o', help='旧配置文件路径')
    parser.add_argument('--new', '-n', help='新配置文件路径')
    parser.add_argument('--output', '-O', help='输出文件路径')
    parser.add_argument('--config', '-c', help='配置文件路径（用于优化/验证）')
    parser.add_argument('--report', '-r', help='生成报告的路径')
    
    args = parser.parse_args()
    
    if args.action == 'merge':
        if not args.old or not args.new or not args.output:
            print("错误：merge 需要指定 --old, --new, --output")
            sys.exit(1)
        
        merger = ConfigMerger(args.old, args.new, args.output)
        if not merger.load_configs():
            sys.exit(1)
        
        merger.merge()
        if not merger.save_merged():
            sys.exit(1)
        
        merger.print_summary()
        
        if args.report:
            merger.generate_report(args.report)
    
    elif args.action == 'optimize':
        config_path = args.config or "_config.next.yml"
        optimizer = ConfigOptimizer(config_path)
        
        if not optimizer.load_config():
            sys.exit(1)
        
        optimizer.optimize()
        if not optimizer.save_optimized():
            sys.exit(1)
    
    elif args.action == 'validate':
        config_path = args.config or "_config.next.yml"
        is_valid, errors = validate_config(config_path)
        
        if is_valid:
            print(f"✓ 配置验证通过：{config_path}")
        else:
            print(f"✗ 配置验证失败：{config_path}")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
    
    print("\n✨ 操作完成！")


if __name__ == "__main__":
    main()
