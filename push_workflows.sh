#!/bin/bash
# 推送 workflows 到 GitHub

echo "🚀 开始推送 workflows..."

# 检查是否在正确的目录
if [ ! -f "_config.yml" ]; then
    echo "❌ 错误：请在 Hexo 博客根目录运行此脚本"
    exit 1
fi

# 查看 git 状态
echo "\n📊 当前 git 状态:"
git status --short

# 添加 workflows
echo "\n📦 添加 workflows 文件..."
git add .github/workflows/

# 检查是否有变更
if git diff --cached --quiet; then
    echo "ℹ️ 没有检测到新的变更"
else
    # 提交
    echo "💾 提交变更..."
    git commit -m "✨ Add AI auto blog workflows"
    
    # 推送
    echo "📤 推送到 GitHub..."
    git push origin master
    
    if [ $? -eq 0 ]; then
        echo "\n✅ 推送成功！"
        echo "\n🔗 接下来请："
        echo "   1. 访问 https://github.com/zzw868/zzw868.github.io/actions"
        echo "   2. 点击 'Global Finance AI Blog'"
        echo "   3. 点击 'Run workflow' 测试"
        echo "   4. 等待 2-3 分钟查看结果"
    else
        echo "\n❌ 推送失败，请检查网络连接和 GitHub 权限"
        exit 1
    fi
fi
