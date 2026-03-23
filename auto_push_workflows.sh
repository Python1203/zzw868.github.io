#!/bin/bash
# 自动推送 Workflows 到 GitHub - 一键执行版

echo "======================================"
echo "🚀 推送 AI Workflows 到 GitHub"
echo "======================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "_config.yml" ]; then
    echo "❌ 错误：请在 Hexo 博客根目录运行此脚本"
    exit 1
fi

echo "✅ 目录检查通过"
echo ""

# 检查工作流文件是否存在
WORKFLOW_FILES=(
    ".github/workflows/finance_auto_blog.yml"
    ".github/workflows/seo-submit.yml"
    ".github/workflows/ai-writer.yml"
)

for file in "${WORKFLOW_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ 找到：$file"
    else
        echo "✗ 缺失：$file"
    fi
done

echo ""
echo "📦 开始添加文件到 git..."
git add .github/workflows/*.yml

echo ""
echo "💾 提交变更..."
git commit -m "✨ Add AI auto blog workflows (finance_auto_blog, seo-submit, ai-writer)"

echo ""
echo "📤 推送到 GitHub..."
git push origin master

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ 推送成功！"
    echo "======================================"
    echo ""
    echo "🔗 接下来请执行以下步骤："
    echo ""
    echo "1️⃣  访问 Actions 页面："
    echo "   https://github.com/zzw868/zzw868.github.io/actions"
    echo ""
    echo "2️⃣  点击左侧的 'Global Finance AI Blog'"
    echo ""
    echo "3️⃣  点击右侧绿色按钮 'Run workflow'"
    echo ""
    echo "4️⃣  再次点击 'Run workflow' 开始执行"
    echo ""
    echo "5️⃣  等待 2-3 分钟查看结果"
    echo ""
    echo "🎉 完成后你的博客将每天自动生成文章！"
    echo ""
else
    echo ""
    echo "======================================"
    echo "❌ 推送失败"
    echo "======================================"
    echo ""
    echo "可能的原因："
    echo "1. 网络连接问题"
    echo "2. GitHub 权限不足"
    echo "3. 远程仓库配置错误"
    echo ""
    echo "请检查后重试，或手动执行 git push"
    exit 1
fi
