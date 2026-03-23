#!/bin/bash
# 紧急手动部署脚本 - 绕过 GitHub Actions 锁定
set -e

echo "============================================================"
echo "🚀 紧急手动部署博客到 GitHub Pages"
echo "============================================================"
echo "时间：$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 清理并生成 Hexo
echo "📦 Step 1: 清理并生成静态文件..."
hexo clean > /dev/null 2>&1
hexo generate > /dev/null 2>&1
echo "✅ Hexo 生成完成 (public/ 目录)"
echo ""

# 2. 重新初始化 .deploy_git
echo "🔄 Step 2: 重新初始化部署仓库..."
rm -rf .deploy_git
hexo deploy --setup > /dev/null 2>&1
echo "✅ 部署仓库初始化完成"
echo ""

# 3. 设置远程仓库（使用 HTTPS 方式，兼容 GitHub Actions）
echo "🔗 Step 3: 配置远程仓库..."
cd .deploy_git
# 优先使用 HTTPS（适合 CI/CD），如果没有 GITHUB_TOKEN 则使用 SSH
current_branch=$(git branch --show-current)
if [ -n "$GITHUB_TOKEN" ]; then
    git remote add origin https://x-access-token:${GITHUB_TOKEN}@github.com/Python1203/zzw868.github.io.git
    echo "✅ 已配置 HTTPS 远程仓库（使用 GITHUB_TOKEN）"
else
    git remote add origin git@github.com:Python1203/zzw868.github.io.git
    echo "✅ 已配置 SSH 远程仓库"
fi
echo ""

# 4. 推送到 gh-pages 分支
echo "🚀 Step 4: 推送到 gh-pages 分支..."
git push -f origin main:gh-pages

echo ""
echo "============================================================"
echo "✨ 部署完成！"
echo "============================================================"
echo ""
echo "🌐 访问地址："
echo "   https://zzw868.github.io"
echo ""
echo "⏰ 等待 1-2 分钟让 GitHub Pages 生效"
echo "💡 提示：强制刷新浏览器 Ctrl+F5"
echo ""
echo "📊 最新文章："
ls -lt ../source/_posts/*.md | head -3 | awk '{print "   - " $9}'
echo ""
