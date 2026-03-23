#!/bin/bash
# AI 自动修复博客更新问题
set -e

echo "============================================================"
echo "🤖 AI 自动修复博客更新"
echo "============================================================"
echo "时间：$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 检查最新文章
echo "📝 检查最新文章..."
LATEST_POST=$(ls -t source/_posts/*.md 2>/dev/null | head -1)
if [ -z "$LATEST_POST" ]; then
    echo "❌ 错误：没有找到文章文件"
    exit 1
fi
echo "✓ 最新文章：$LATEST_POST"
echo ""

# 2. Hexo 清理和生成
echo "🔧 清理并生成静态文件..."
hexo clean > /dev/null 2>&1
hexo generate > /dev/null 2>&1
echo "✓ Hexo 生成完成"
echo ""

# 3. 检查生成的文件
echo "📄 检查生成的文件..."
GENERATED_COUNT=$(find public -name "*.html" | wc -l | tr -d ' ')
echo "✓ 已生成 $GENERATED_COUNT 个 HTML 文件"
echo ""

# 4. 添加到 Git 提交
echo "💾 准备提交变更..."
git add -A
CHANGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
if [ "$CHANGED" -eq 0 ]; then
    echo "⏭️  没有变更需要提交"
else
    git commit -m "🤖 AI 自动修复：更新博客内容 $(date '+%Y-%m-%d %H:%M')"
    echo "✓ 已提交 $CHANGED 个文件的变更"
fi
echo ""

# 5. 推送到 GitHub
echo "🚀 推送到 GitHub..."
git push origin master
echo "✓ 推送成功"
echo ""

# 6. 输出访问地址
echo "============================================================"
echo "✨ 修复完成！"
echo "============================================================"
echo ""
echo "🌐 访问地址："
echo "   https://python1203.github.io/zzw868.github.io/"
echo ""
echo "📊 最新文章："
ls -lt source/_posts/*.md | head -3 | awk '{print "   - " $9}'
echo ""
echo "⏰ GitHub Actions 将在以下时间自动更新："
echo "   周一至周五 北京时间 16:10"
echo ""
echo "💡 提示："
echo "   - 等待 1-2 分钟让 GitHub Pages 生效"
echo "   - 强制刷新浏览器缓存 (Ctrl+F5)"
echo "   - 查看 Actions 状态：https://github.com/Python1203/zzw868.github.io/actions"
echo ""
