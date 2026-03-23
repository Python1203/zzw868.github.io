#!/bin/bash
# AI 自动创作一键执行脚本

echo "🚀 开始 AI 自动创作..."

# 检查环境变量
if [ -z "$AI_API_KEY" ]; then
    echo "❌ 错误：未设置 AI_API_KEY"
    echo "请先设置环境变量："
    echo "  export AI_API_KEY='sk-your-key'"
    echo "  export AI_BASE_URL='https://xh.v1api.cc'"
    exit 1
fi

# 安装依赖
echo "📦 检查依赖..."
pip install openai -q 2>/dev/null

# 运行 AI 创作
echo "🤖 AI 正在创作中..."
python scripts/ai_writer.py --count 1

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ AI 创作成功！"
    echo ""
    echo "📝 接下来可以："
    echo "   1. hexo generate  # 生成静态文件"
    echo "   2. hexo deploy    # 部署到 GitHub Pages"
    echo ""
else
    echo ""
    echo "❌ AI 创作失败，请检查 API Key 和网络连接"
    exit 1
fi
