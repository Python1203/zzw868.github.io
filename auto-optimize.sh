#!/bin/bash
# AI 自动优化 - 一键删除冗余代码
# 安全、快速、自动化

set -e

echo ""
echo "============================================================"
echo "🤖 AI 自动优化 - 删除冗余代码"
echo "============================================================"
echo "开始时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "错误：请在项目根目录运行此脚本"
    exit 1
fi

# 创建 Git 备份提示
echo "💡 提示：建议先执行 Git 提交以备份当前状态"
read -p "是否继续？(y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "✓ 操作已取消"
    exit 0
fi

echo ""
echo "============================================================"
echo "📊 步骤 1: 查找并删除备份文件"
echo "============================================================"

# 查找备份文件
BACKUP_FILES=$(find . -type f \( -name "*.backup" -o -name "*.bak" -o -name "*.old" -o -name "*~" \) \
    -not -path "./.venv/*" \
    -not -path "./node_modules/*" \
    -not -path "./financial-ai-dashboard/backend/venv/*" \
    -not -path "./financial-ai-dashboard/backend/venv312/*" \
    2>/dev/null || true)

if [ -z "$BACKUP_FILES" ]; then
    echo "✓ 没有发现备份文件"
else
    BACKUP_COUNT=$(echo "$BACKUP_FILES" | wc -l | tr -d ' ')
    echo "发现 $BACKUP_COUNT 个备份文件:"
    echo "$BACKUP_FILES" | while read -r file; do
        if [ -n "$file" ]; then
            SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
            echo "  🗑️  删除：$file ($SIZE bytes)"
            rm -f "$file"
        fi
    done
    echo "✓ 备份文件已删除"
fi

echo ""
echo "============================================================"
echo "🎨 步骤 2: 运行 Python 优化脚本"
echo "============================================================"

# 运行 Python 优化脚本
python3 auto_optimize_now.py <<EOF
y
EOF

echo ""
echo "============================================================"
echo "✨ 优化完成！"
echo "============================================================"
echo "结束时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "📄 查看优化报告："
echo "   - redundancy_report.md (检测报告)"
echo "   - ai_optimization_report.md (优化报告)"
echo ""
echo "💡 提示："
echo "   - 使用 'git status' 查看变更"
echo "   - 使用 'git diff' 查看详细修改"
echo "   - 如有需要，使用 'git checkout' 恢复文件"
echo ""
