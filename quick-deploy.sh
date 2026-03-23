#!/bin/bash
# ===============================================================
# 快速部署博客到 GitHub Pages
# 用于解决首页和目录不显示更新内容的问题
# ===============================================================

set -e

echo "============================================================"
echo "🚀 快速部署博客到 GitHub Pages"
echo "============================================================"

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "错误：请在博客根目录运行此脚本"
    exit 1
fi

# 检查 Git 凭证
echo ""
echo "ℹ️  提示：此脚本需要 GitHub 访问权限"
echo "   方式 1: 配置 SSH Key（推荐）"
echo "   方式 2: 使用 HTTPS + Token"
echo ""

# 清理旧文件
echo "📦 步骤 1: 清理旧文件..."
hexo clean
echo "✓ 清理完成"

# 生成新文件
echo ""
echo "📝 步骤 2: 生成静态文件..."
hexo generate
echo "✓ 生成完成"

# 检查 .deploy_git 目录
if [ ! -d ".deploy_git" ]; then
    echo "✗ 错误：.deploy_git 目录不存在"
    echo "   请先运行：hexo deploy 初始化部署目录"
    exit 1
fi

# 进入部署目录
echo ""
echo "📂 步骤 3: 准备部署文件..."
cd .deploy_git

# 添加所有文件
git add -A

# 检查是否有变更
if git diff-index --quiet HEAD; then
    echo "ℹ️  没有检测到变更，无需提交"
    cd ..
    exit 0
fi

# 提交变更
echo "💾 步骤 4: 提交变更..."
git commit -m "🤖 auto deploy: $(date '+%Y-%m-%d %H:%M:%S')"

# 推送到 GitHub
echo ""
echo "⬆️  步骤 5: 推送到 GitHub..."
echo "   目标：origin gh-pages"
echo ""

# 尝试推送
if git push origin gh-pages 2>&1; then
    echo ""
    echo "============================================================"
    echo "✨ 部署成功！"
    echo "============================================================"
    echo ""
    echo "📱 查看网站："
    echo "   https://zzw868.github.io"
    echo ""
    echo "⏰ 提示：GitHub Pages 可能需要 1-2 分钟生效"
    echo ""
else
    echo ""
    echo "============================================================"
    echo "⚠️  推送失败"
    echo "============================================================"
    echo ""
    echo "可能的原因："
    echo "  1. 未配置 SSH Key"
    echo "  2. GitHub Token 过期"
    echo "  3. 网络连接问题"
    echo ""
    echo "解决方案："
    echo "  方案 1: 配置 SSH Key"
    echo "    ssh-keygen -t ed25519 -C \"your_email@example.com\""
    echo "    然后到 GitHub 设置中添加公钥"
    echo ""
    echo "  方案 2: 使用 Token"
    echo "    修改 _config.yml 中的 deploy.repo 为："
    echo "    repo: https://<TOKEN>@github.com/Python1203/zzw868.github.io.git"
    echo ""
    echo "  方案 3: 手动推送"
    echo "    cd .deploy_git"
    echo "    git push origin gh-pages"
    echo ""
    cd ..
    exit 1
fi

cd ..

echo "============================================================"
echo "✅ 所有操作完成！"
echo "============================================================"
