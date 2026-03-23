#!/bin/bash
# GitHub Actions 状态检查脚本

echo "======================================"
echo "🔍 检查 GitHub Actions 配置"
echo "======================================"
echo ""

# 1. 检查是否在 master 分支
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "📌 当前分支：$CURRENT_BRANCH"
if [ "$CURRENT_BRANCH" != "master" ]; then
    echo "⚠️  警告：不在 master 分支！"
else
    echo "✅ 在正确的分支"
fi
echo ""

# 2. 检查工作流文件是否存在
echo "📁 工作流文件检查："
WORKFLOW_FILES=(
    ".github/workflows/finance_auto_blog.yml"
    ".github/workflows/seo-submit.yml"
    ".github/workflows/ai-writer.yml"
)

for file in "${WORKFLOW_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (缺失)"
    fi
done
echo ""

# 3. 检查 git 状态
echo "📊 Git 状态："
git status --short
if [ $? -eq 0 ]; then
    echo "✅ Git 仓库正常"
else
    echo "❌ Git 仓库有问题"
fi
echo ""

# 4. 查看最近的提交
echo "📝 最近 5 次提交："
git log --oneline -5
echo ""

# 5. 检查远程仓库 URL
echo "🌐 远程仓库："
git remote -v
echo ""

# 6. 生成报告
echo "======================================"
echo "📋 诊断报告"
echo "======================================"
echo ""

if [ "$CURRENT_BRANCH" == "master" ]; then
    echo "✅ 分支正确 (master)"
else
    echo "❌ 分支错误，当前在：$CURRENT_BRANCH"
    echo "   运行：git checkout master"
fi

ALL_FILES_EXIST=true
for file in "${WORKFLOW_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        ALL_FILES_EXIST=false
        break
    fi
done

if [ "$ALL_FILES_EXIST" == true ]; then
    echo "✅ 所有工作流文件存在"
else
    echo "❌ 缺少工作流文件"
fi

echo ""
echo "🔗 下一步："
echo "   1. 访问 https://github.com/zzw868/zzw868.github.io/actions"
echo "   2. 查看是否还有 404 错误"
echo "   3. 如果没有 404，点击 'Run workflow' 测试"
echo ""
