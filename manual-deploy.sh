#!/bin/bash
# 手动部署博客到 GitHub Pages（绕过 Actions 锁定）
set -e

echo "🚀 开始手动部署博客..."
echo ""

# 1. 清理并生成
echo "📦 Step 1: 清理并生成静态文件..."
hexo clean > /dev/null 2>&1
hexo generate > /dev/null 2>&1
echo "✅ Hexo 生成完成"
echo ""

# 2. 进入 .deploy_git 目录
echo "📂 Step 2: 准备部署文件..."
cd .deploy_git

# 3. 添加所有文件
git add -A

# 4. 检查是否有变更
if git diff --staged --quiet; then
    echo "⏭️  没有变更，跳过部署"
    exit 0
fi

# 5. 提交变更
git commit -m "🤖 手动部署：$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')"
echo "✅ 提交完成"
echo ""

# 6. 推送到 GitHub
echo "🚀 Step 3: 推送到 GitHub..."
git push origin main -f

echo ""
echo "============================================================"
echo "✨ 部署完成！"
echo "============================================================"
echo ""
echo "🌐 访问地址："
echo "   https://zzw868.github.io"
echo ""
echo "⏰ 等待 1-2 分钟让 GitHub Pages 生效"
echo "💡 提示：强制刷新浏览器 (Ctrl+F5)"
echo ""
