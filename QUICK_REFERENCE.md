# AI 自动优化 - 快速参考卡

## 🚀 一键优化（推荐）

```bash
./auto-optimize.sh
```

## 📊 分步操作

### 1. 检测扫描（不修改）
```bash
python3 auto_remove_redundancy.py --scan
```

### 2. 执行优化（实际修改）
```bash
python3 auto_optimize_now.py
```

## 📈 查看报告

```bash
# 检测报告（问题列表）
cat redundancy_report.md

# 优化报告（已完成的操作）
cat ai_optimization_report.md

# 执行总结
cat OPTIMIZATION_SUMMARY.md
```

## 🔍 检查变更

```bash
# 查看哪些文件被修改
git status

# 查看具体修改内容
git diff

# 恢复某个文件
git checkout HEAD -- path/to/file
```

## 📦 主要功能

| 功能 | 说明 | 效果 |
|------|------|------|
| 删除备份文件 | .backup, .bak, .old | 节省空间 |
| 清空 HTML 标签 | div, span, p | 减少冗余 |
| 重复 class 值 | 自动去重 | 精简代码 |
| 无用注释 | Author, Copyright | 清理元数据 |
| Python 导入 | 未使用的 import | 提升性能 |

## ⚡ 常用命令

```bash
# 只删除备份文件（预览）
python3 auto_remove_redundancy.py --delete-backups

# 优化单个 HTML 文件
python3 auto_remove_redundancy.py --optimize file.html

# 自定义报告路径
python3 auto_remove_redundancy.py --scan --report my_report.md

# 添加执行权限
chmod +x auto-optimize.sh
```

## 🎯 预期效果

根据本次优化：
- **删除备份**: ~240KB
- **HTML 优化**: ~0.5KB
- **Python 清理**: 9 个导入
- **总节省**: ~240KB

## ⚠️ 注意事项

1. ✅ 先 Git 提交备份
2. ✅ 检查 git diff
3. ✅ 测试网站功能
4. ✅ 有异常就恢复

## 🔄 恢复方法

```bash
# 恢复所有变更
git checkout HEAD -- .

# 或恢复单个文件
git checkout HEAD -- path/to/file
```

## 📚 完整文档

- `AI_OPTIMIZATION_GUIDE.md` - 详细使用指南
- `redundancy_report.md` - 问题检测报告
- `ai_optimization_report.md` - 优化结果报告
- `OPTIMIZATION_SUMMARY.md` - 执行总结

---

**版本**: 1.0.0 | **更新**: 2026-03-18
