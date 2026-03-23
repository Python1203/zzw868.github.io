#!/bin/bash
# 使用百度文心 API 运行 AI Writer

echo "🚀 使用百度文心 API 生成文章..."

# 检查参数
API_KEY="${1:-}"
SECRET_KEY="${2:-}"

if [ -z "$API_KEY" ]; then
    echo "❌ 错误：请提供 API Key"
    echo ""
    echo "用法："
    echo "  ./run_baidu_ai.sh <API_Key> <Secret_Key>"
    echo ""
    echo "或者先设置环境变量："
    echo "  export BAIDU_API_KEY='your-key'"
    echo "  export BAIDU_SECRET_KEY='your-secret'"
    echo "  ./run_baidu_ai.sh"
    exit 1
fi

# 设置环境变量
export AI_API_KEY="$API_KEY"
export AI_SECRET_KEY="${SECRET_KEY:-}"
export AI_BASE_URL="https://qianfan.baidubce.com/v2"

# 运行 AI Writer
echo ""
echo "📝 开始生成文章..."
python tools/ai_writer.py --count 1

echo ""
echo "✅ 完成！"
