#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 驱动的配置优化检查与报告生成器
用于检测 Next 主题配置问题并生成详细报告
"""

import yaml
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class SeverityLevel(Enum):
    """问题严重程度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Issue:
    """配置问题"""
    code: str
    message: str
    severity: SeverityLevel
    path: str
    suggestion: str
    current_value: Any = None
    recommended_value: Any = None


class ConfigChecker:
    """配置检查器"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = {}
        self.issues: List[Issue] = []
        
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            print(f"✓ 已加载配置：{self.config_path}")
            return True
        except Exception as e:
            print(f"✗ 加载失败：{str(e)}")
            return False
    
    def check_all(self) -> List[Issue]:
        """执行所有检查"""
        print("\n🔍 开始检查配置...\n")
        
        self._check_scheme()
        self._check_menu()
        self._check_sidebar()
        self._check_darkmode()
        self._check_search()
        self._check_performance()
        self._check_seo()
        self._check_customization()
        
        print(f"✓ 检查完成，发现 {len(self.issues)} 个问题\n")
        return self.issues
    
    def _add_issue(self, issue: Issue):
        """添加问题"""
        self.issues.append(issue)
    
    def _check_scheme(self):
        """检查主题方案"""
        scheme = self.config.get('scheme', 'Muse')
        valid_schemes = ['Muse', 'Mist', 'Pisces', 'Gemini']
        
        if scheme not in valid_schemes:
            self._add_issue(Issue(
                code="SCHEME_001",
                message=f"无效的主题方案：{scheme}",
                severity=SeverityLevel.ERROR,
                path="scheme",
                suggestion=f"使用有效的方案：{', '.join(valid_schemes)}",
                current_value=scheme,
                recommended_value="Muse"
            ))
        else:
            # 推荐 Gemini（功能最丰富）
            if scheme != 'Gemini':
                self._add_issue(Issue(
                    code="SCHEME_002",
                    message=f"当前方案：{scheme}，推荐升级到 Gemini",
                    severity=SeverityLevel.INFO,
                    path="scheme",
                    suggestion="Gemini 方案提供更多的功能和更好的用户体验",
                    current_value=scheme,
                    recommended_value="Gemini"
                ))
    
    def _check_menu(self):
        """检查菜单配置"""
        menu = self.config.get('menu', {})
        
        if not menu:
            self._add_issue(Issue(
                code="MENU_001",
                message="菜单未配置",
                severity=SeverityLevel.WARNING,
                path="menu",
                suggestion="至少配置首页和归档页",
                current_value={},
                recommended_value={"home": "/ || fa fa-home", "archives": "/archives/ || fa fa-archive"}
            ))
        else:
            # 检查必要页面
            required_pages = ['home', 'archives']
            for page in required_pages:
                if page not in menu:
                    self._add_issue(Issue(
                        code="MENU_002",
                        message=f"缺少必要的菜单项：{page}",
                        severity=SeverityLevel.WARNING,
                        path=f"menu.{page}",
                        suggestion=f"添加 {page} 菜单项",
                        current_value=None,
                        recommended_value=f"{page}: /{page}/ || fa fa-{page}"
                    ))
    
    def _check_sidebar(self):
        """检查侧边栏配置"""
        sidebar = self.config.get('sidebar', {})
        
        # 检查位置
        position = sidebar.get('position', 'left')
        if position not in ['left', 'right']:
            self._add_issue(Issue(
                code="SIDEBAR_001",
                message=f"无效的侧边栏位置：{position}",
                severity=SeverityLevel.ERROR,
                path="sidebar.position",
                suggestion="使用 left 或 right",
                current_value=position,
                recommended_value="left"
            ))
        
        # 检查显示模式
        display = sidebar.get('display', 'post')
        valid_displays = ['post', 'always', 'hide', 'remove']
        if display not in valid_displays:
            self._add_issue(Issue(
                code="SIDEBAR_002",
                message=f"无效的侧边栏显示模式：{display}",
                severity=SeverityLevel.ERROR,
                path="sidebar.display",
                suggestion=f"使用有效的模式：{', '.join(valid_displays)}",
                current_value=display,
                recommended_value="always"
            ))
        elif display == 'post':
            self._add_issue(Issue(
                code="SIDEBAR_003",
                message="侧边栏仅在文章页显示，推荐设置为 always",
                severity=SeverityLevel.INFO,
                path="sidebar.display",
                suggestion="设置为 always 以在所有页面显示侧边栏",
                current_value=display,
                recommended_value="always"
            ))
        
        # 检查移动端设置
        onmobile = sidebar.get('onmobile', False)
        if not onmobile:
            self._add_issue(Issue(
                code="SIDEBAR_004",
                message="移动端未启用侧边栏",
                severity=SeverityLevel.INFO,
                path="sidebar.onmobile",
                suggestion="在移动端也显示侧边栏以提升用户体验",
                current_value=onmobile,
                recommended_value=True
            ))
    
    def _check_darkmode(self):
        """检查暗色模式"""
        darkmode = self.config.get('darkmode', False)
        
        if not darkmode:
            self._add_issue(Issue(
                code="DARKMODE_001",
                message="未启用暗色模式",
                severity=SeverityLevel.INFO,
                path="darkmode",
                suggestion="启用暗色模式以提升夜间阅读体验",
                current_value=darkmode,
                recommended_value=True
            ))
    
    def _check_search(self):
        """检查搜索配置"""
        local_search = self.config.get('local_search', {})
        
        enable = local_search.get('enable', False)
        if not enable:
            self._add_issue(Issue(
                code="SEARCH_001",
                message="未启用本地搜索",
                severity=SeverityLevel.WARNING,
                path="local_search.enable",
                suggestion="启用本地搜索以提升用户体验",
                current_value=enable,
                recommended_value=True
            ))
        else:
            # 检查预加载
            preload = local_search.get('preload', False)
            if not preload:
                self._add_issue(Issue(
                    code="SEARCH_002",
                    message="搜索未启用预加载",
                    severity=SeverityLevel.INFO,
                    path="local_search.preload",
                    suggestion="启用预加载以加快搜索速度",
                    current_value=preload,
                    recommended_value=True
                ))
    
    def _check_performance(self):
        """检查性能相关配置"""
        # 检查缓存
        cache = self.config.get('cache', {})
        if isinstance(cache, dict):
            cache_enable = cache.get('enable', True)
        else:
            cache_enable = cache
        
        if not cache_enable:
            self._add_issue(Issue(
                code="PERF_001",
                message="未启用内容生成缓存",
                severity=SeverityLevel.WARNING,
                path="cache.enable",
                suggestion="启用缓存以加快 Hexo 生成速度",
                current_value=cache_enable,
                recommended_value=True
            ))
        
        # 检查压缩
        minify = self.config.get('minify', False)
        if not minify:
            self._add_issue(Issue(
                code="PERF_002",
                message="未启用文件压缩",
                severity=SeverityLevel.INFO,
                path="minify",
                suggestion="启用文件压缩以减少文件大小",
                current_value=minify,
                recommended_value=True
            ))
    
    def _check_seo(self):
        """检查 SEO 相关配置"""
        # 检查 canonical
        canonical = self.config.get('canonical', False)
        if not canonical:
            self._add_issue(Issue(
                code="SEO_001",
                message="未启用 canonical URL",
                severity=SeverityLevel.WARNING,
                path="canonical",
                suggestion="启用 canonical URL 以避免 SEO 重复内容问题",
                current_value=canonical,
                recommended_value=True
            ))
        
        # 检查 RSS
        # 这个通常在主配置文件，但可以提醒
        
    def _check_customization(self):
        """检查自定义配置"""
        custom_files = self.config.get('custom_file_path', {})
        
        # 检查是否使用了自定义文件
        if not custom_files:
            self._add_issue(Issue(
                code="CUSTOM_001",
                message="未使用自定义文件注入",
                severity=SeverityLevel.INFO,
                path="custom_file_path",
                suggestion="使用 source/_data 目录来自定义主题样式和功能",
                current_value=None,
                recommended_value={
                    'sidebar': 'source/_data/sidebar.njk',
                    'style': 'source/_data/custom.styl'
                }
            ))
    
    def get_issues_by_severity(self, severity: SeverityLevel) -> List[Issue]:
        """按严重程度获取问题"""
        return [i for i in self.issues if i.severity == severity]
    
    def get_summary(self) -> Dict[str, int]:
        """获取摘要统计"""
        summary = {
            'total': len(self.issues),
            'critical': len(self.get_issues_by_severity(SeverityLevel.CRITICAL)),
            'error': len(self.get_issues_by_severity(SeverityLevel.ERROR)),
            'warning': len(self.get_issues_by_severity(SeverityLevel.WARNING)),
            'info': len(self.get_issues_by_severity(SeverityLevel.INFO))
        }
        return summary


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, checker: ConfigChecker):
        self.checker = checker
        
    def generate_markdown_report(self, output_path: str) -> bool:
        """生成 Markdown 格式报告"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            summary = self.checker.get_summary()
            
            report = f"""# 🔍 Next 主题配置检查报告

## 📅 基本信息

- **生成时间**: {timestamp}
- **配置文件**: {self.checker.config_path}
- **检查项目**: 9 大类配置检查

## 📊 问题摘要

| 严重程度 | 数量 |
|---------|------|
| 🔴 严重 (Critical) | {summary['critical']} |
| 🟠 错误 (Error) | {summary['error']} |
| 🟡 警告 (Warning) | {summary['warning']} |
| 🔵 提示 (Info) | {summary['info']} |
| **总计** | **{summary['total']}** |

## 📋 详细问题列表

"""
            
            # 按严重程度分组显示
            for severity in [SeverityLevel.CRITICAL, SeverityLevel.ERROR, SeverityLevel.WARNING, SeverityLevel.INFO]:
                issues = self.checker.get_issues_by_severity(severity)
                if not issues:
                    continue
                
                severity_icons = {
                    SeverityLevel.CRITICAL: "🔴",
                    SeverityLevel.ERROR: "🟠",
                    SeverityLevel.WARNING: "🟡",
                    SeverityLevel.INFO: "🔵"
                }
                
                report += f"### {severity_icons[severity]} {severity.value.upper()} ({len(issues)})\n\n"
                
                for issue in issues:
                    report += f"#### [{issue.code}] {issue.message}\n\n"
                    report += f"- **路径**: `{issue.path}`\n"
                    report += f"- **当前值**: `{issue.current_value}`\n"
                    if issue.recommended_value:
                        report += f"- **推荐值**: `{issue.recommended_value}`\n"
                    report += f"- **建议**: {issue.suggestion}\n\n"
                    report += "---\n\n"
            
            # 添加优化建议
            report += """## 💡 总体建议

### 立即修复的问题
"""
            
            critical_issues = self.checker.get_issues_by_severity(SeverityLevel.CRITICAL)
            error_issues = self.checker.get_issues_by_severity(SeverityLevel.ERROR)
            
            if critical_issues or error_issues:
                for issue in critical_issues + error_issues[:5]:
                    report += f"- [ ] 修复 {issue.code}: {issue.message}\n"
            else:
                report += "*没有需要立即修复的问题*\n"
            
            report += """
### 推荐优化的项目
"""
            warning_issues = self.checker.get_issues_by_severity(SeverityLevel.WARNING)
            info_issues = self.checker.get_issues_by_severity(SeverityLevel.INFO)
            
            for issue in warning_issues + info_issues[:10]:
                report += f"- [ ] {issue.code}: {issue.message}\n"
            
            report += f"""
## 🎯 下一步行动

1. **优先修复**: 处理所有严重和错误级别的问题
2. **逐步优化**: 根据建议调整警告和提示级别的问题
3. **测试验证**: 运行 `hexo clean && hexo g` 测试网站
4. **持续改进**: 定期检查配置，保持最佳状态

---
*此报告由 AI 配置检查器自动生成*
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"✓ 报告已生成：{output_path}")
            return True
            
        except Exception as e:
            print(f"✗ 生成报告失败：{str(e)}")
            return False
    
    def generate_json_report(self, output_path: str) -> bool:
        """生成 JSON 格式报告"""
        try:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'config_path': self.checker.config_path,
                'summary': self.checker.get_summary(),
                'issues': [
                    {
                        'code': issue.code,
                        'message': issue.message,
                        'severity': issue.severity.value,
                        'path': issue.path,
                        'suggestion': issue.suggestion,
                        'current_value': issue.current_value,
                        'recommended_value': issue.recommended_value
                    }
                    for issue in self.checker.issues
                ]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ JSON 报告已生成：{output_path}")
            return True
            
        except Exception as e:
            print(f"✗ 生成 JSON 报告失败：{str(e)}")
            return False
    
    def print_console_report(self):
        """在控制台打印简要报告"""
        summary = self.checker.get_summary()
        
        print("\n" + "=" * 60)
        print("📊 配置检查摘要")
        print("=" * 60)
        print(f"总问题数：{summary['total']}")
        print(f"  🔴 严重：{summary['critical']}")
        print(f"  🟠 错误：{summary['error']}")
        print(f"  🟡 警告：{summary['warning']}")
        print(f"  🔵 提示：{summary['info']}")
        print("=" * 60)
        
        if summary['critical'] > 0 or summary['error'] > 0:
            print("\n⚠️  发现严重问题，建议立即修复！\n")
            for issue in self.checker.get_issues_by_severity(SeverityLevel.CRITICAL) + \
                         self.checker.get_issues_by_severity(SeverityLevel.ERROR)[:3]:
                print(f"  - [{issue.code}] {issue.message}")
        elif summary['warning'] > 0:
            print("\n💡 发现可优化的项目\n")
            for issue in self.checker.get_issues_by_severity(SeverityLevel.WARNING)[:3]:
                print(f"  - [{issue.code}] {issue.message}")
        else:
            print("\n✅ 配置状态良好！\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI 配置检查与报告生成器')
    parser.add_argument('config', nargs='?', default='_config.next.yml',
                       help='配置文件路径')
    parser.add_argument('--output', '-o', help='报告输出路径')
    parser.add_argument('--format', '-f', choices=['markdown', 'json', 'both'],
                       default='markdown', help='报告格式')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='静默模式，仅输出报告')
    
    args = parser.parse_args()
    
    # 检查配置文件是否存在
    if not os.path.exists(args.config):
        print(f"✗ 配置文件不存在：{args.config}")
        sys.exit(1)
    
    # 创建检查器
    checker = ConfigChecker(args.config)
    if not checker.load_config():
        sys.exit(1)
    
    # 执行检查
    checker.check_all()
    
    # 创建报告生成器
    generator = ReportGenerator(checker)
    
    if not args.quiet:
        generator.print_console_report()
    
    # 生成报告文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if args.format in ['markdown', 'both']:
        output_md = args.output or f"config_check_report_{timestamp}.md"
        generator.generate_markdown_report(output_md)
    
    if args.format in ['json', 'both']:
        output_json = args.output.replace('.md', '.json') if args.output else f"config_check_report_{timestamp}.json"
        generator.generate_json_report(output_json)
    
    # 根据问题数量设置退出码
    summary = checker.get_summary()
    if summary['critical'] > 0 or summary['error'] > 0:
        sys.exit(2)
    elif summary['warning'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
