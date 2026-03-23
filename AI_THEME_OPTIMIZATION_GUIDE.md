# 🤖 AI 自动优化修复 Next 主题工具

## 📋 简介

这是一套完整的 AI 驱动工具，用于自动优化、修复和更新 Hexo Next 主题。集成了配置检查、智能合并、自动优化、版本更新和报告生成等功能。

## 🎯 核心功能

### 1. 一键完整优化
- ✅ 自动检查系统依赖
- ✅ 完整备份当前配置
- ✅ 智能扫描配置问题
- ✅ 自动优化配置项
- ✅ 检查并更新主题版本
- ✅ 清理冗余文件
- ✅ 生成详细报告

### 2. 配置智能检查
- 🔍 9 大类配置检查
- 🎯 4 个严重程度级别
- 📊 详细的问题定位
- 💡 智能优化建议

### 3. 配置智能合并
- 🔄 深度合并新旧配置
- 🔒 保留用户自定义
- ➕ 自动补充新配置项
- 📝 记录所有变更

### 4. 主题自动更新
- 📦 检测最新版本
- 💾 自动备份旧版本
- ⬇️ 安全更新主题
- ✅ 验证更新结果

### 5. 报告生成
- 📄 Markdown 格式报告
- 📊 JSON 格式数据
- 🖥️ 控制台摘要输出
- 📈 统计信息可视化

## 🚀 快速开始

### 方法一：一键自动优化（推荐）

```bash
# 赋予执行权限
chmod +x ai-optimize-next-theme.sh

# 运行一键优化（自动模式）
./ai-optimize-next-theme.sh auto
```

### 方法二：交互式菜单

```bash
# 运行交互模式
./ai-optimize-next-theme.sh

# 然后选择选项 1: 一键完整优化
```

### 方法三：分步执行

```bash
# 1. 检查配置
./ai-optimize-next-theme.sh check

# 2. 优化配置
./ai-optimize-next-theme.sh optimize

# 3. 更新主题
./ai-optimize-next-theme.sh update

# 4. 备份
./ai-optimize-next-theme.sh backup

# 5. 清理
./ai-optimize-next-theme.sh clean

# 6. 生成报告
./ai-optimize-next-theme.sh report
```

## 📁 工具说明

### 主脚本：`ai-optimize-next-theme.sh`

综合性的优化脚本，提供以下功能：

```bash
用法：./ai-optimize-next-theme.sh [选项]

选项:
  auto        自动模式（无需交互，适合 CI/CD）
  check       仅检查配置
  optimize    仅优化配置
  update      检查并更新主题
  backup      完整备份
  clean       清理冗余文件
  report      生成综合报告
  menu        显示交互菜单（默认）
  help        显示帮助信息
```

### 辅助脚本：`auto-update-next-theme.sh`

专注于主题更新的脚本：

```bash
用法：./auto-update-next-theme.sh [选项]

选项:
  check       检查是否有新版本
  backup      仅备份当前配置
  update      完整更新（备份 + 更新 + 验证）
  restore     恢复备份
  report      生成更新报告
  interactive 交互模式（默认）
```

### Python 工具：`smart_merge_config.py`

配置智能合并工具：

```bash
用法：python3 smart_merge_config.py <操作> [选项]

操作:
  merge       合并新旧配置
  optimize    优化配置
  validate    验证配置

示例:
  # 合并配置
  python3 smart_merge_config.py merge \
    --old _config.next.yml.old \
    --new themes/next/_config.yml \
    --output _config.next.yml.merged
  
  # 优化配置
  python3 smart_merge_config.py optimize --config _config.next.yml
  
  # 验证配置
  python3 smart_merge_config.py validate --config _config.next.yml
```

### Python 工具：`config_checker.py`

配置检查与报告生成器：

```bash
用法：python3 config_checker.py [配置文件] [选项]

选项:
  --output, -o    报告输出路径
  --format, -f    报告格式 (markdown/json/both)
  --quiet, -q     静默模式

示例:
  # 检查配置并生成报告
  python3 config_checker.py _config.next.yml --format both
  
  # 静默检查
  python3 config_checker.py _config.next.yml --quiet
```

## 🔧 依赖要求

### 系统要求
- **Node.js**: >= 14.x
- **npm**: >= 6.x
- **Git**: 任意版本
- **Python**: >= 3.7

### Python 依赖
```bash
pip3 install pyyaml
```

### 检查依赖
```bash
./ai-optimize-next-theme.sh auto  # 会自动检查
```

## 📊 配置检查项目

### 1. 主题方案 (Scheme)
- ✓ 检查方案有效性
- ✓ 推荐最佳方案

### 2. 菜单配置 (Menu)
- ✓ 检查必要页面
- ✓ 图标配置

### 3. 侧边栏 (Sidebar)
- ✓ 位置设置
- ✓ 显示模式
- ✓ 移动端适配

### 4. 暗色模式 (Darkmode)
- ✓ 启用状态
- ✓ 兼容性

### 5. 搜索功能 (Search)
- ✓ 本地搜索
- ✓ 预加载

### 6. 性能优化 (Performance)
- ✓ 缓存设置
- ✓ 文件压缩

### 7. SEO 优化 (SEO)
- ✓ Canonical URL
- ✓ 元标签

### 8. 自定义配置 (Customization)
- ✓ 自定义文件注入
- ✓ 样式定制

## 📂 备份管理

### 备份位置
```
.theme_backups/
├── backup_20260319_123456/    # 配置备份
├── full_backup_20260319_123456/ # 完整备份
├── theme_backup_20260319_123456/ # 主题备份
└── config_merges/              # 配置合并备份
```

### 恢复备份
```bash
# 使用主脚本恢复
./ai-optimize-next-theme.sh
# 选择选项 8: 恢复备份

# 或使用更新脚本恢复
./auto-update-next-theme.sh restore
```

## 📝 生成的报告

### 配置检查报告
- `config_check_report_YYYYMMDD_HHMMSS.md`
- `config_check_report_YYYYMMDD_HHMMSS.json`

### 优化报告
- `ai_optimization_report_YYYYMMDD_HHMMSS.md`

### 更新报告
- `ai_theme_update_report_YYYYMMDD_HHMMSS.md`

## 🎯 最佳实践

### 1. 定期更新
```bash
# 每周检查一次更新
./ai-optimize-next-theme.sh update
```

### 2. 修改前备份
```bash
# 每次修改配置前备份
./ai-optimize-next-theme.sh backup
```

### 3. 更新后测试
```bash
# 更新后测试网站
hexo clean && hexo g -d
```

### 4. 查看报告
```bash
# 定期检查生成的报告
cat ai_optimization_report_*.md
```

## 🔗 自动化集成

### GitHub Actions
可以配置定时任务自动检查和更新：

```yaml
name: Auto Update Next Theme

on:
  schedule:
    - cron: '0 0 * * 0'  # 每周日 UTC 0 点

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install
      
      - name: Check and update theme
        run: |
          chmod +x ai-optimize-next-theme.sh
          ./ai-optimize-next-theme.sh auto
      
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "🤖 AI 自动优化 Next 主题" || exit 0
          git push
```

### 本地定时任务
```bash
# 添加到 crontab
crontab -e

# 每周检查一次
0 9 * * 1 cd /path/to/blog && ./ai-optimize-next-theme.sh auto
```

## 🐛 故障排除

### 问题 1: 权限错误
```bash
# 解决方案：赋予执行权限
chmod +x ai-optimize-next-theme.sh
chmod +x auto-update-next-theme.sh
```

### 问题 2: Python 依赖缺失
```bash
# 安装 PyYAML
pip3 install pyyaml
```

### 问题 3: 备份恢复失败
```bash
# 检查备份目录
ls -la .theme_backups/

# 手动恢复
cp .theme_backups/backup_*/_config.next.yml .
```

### 问题 4: 更新失败
```bash
# 清除 npm 缓存
npm cache clean --force

# 重新安装
rm -rf themes/next
npm install hexo-theme-next@latest
```

## 📖 相关资源

- [Next 主题官方文档](https://theme-next.js.org)
- [Next 主题 GitHub](https://github.com/next-theme/hexo-theme-next)
- [Hexo 官方文档](https://hexo.io)
- [配置指南](https://theme-next.js.org/docs/getting-started/configuration)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这些工具！

## 📄 许可证

本工具集遵循与 Next 主题相同的许可证。

---

*最后更新：2026-03-19*
*维护者：AI 自动优化系统*
