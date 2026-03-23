#!/bin/bash

# AI 聊天机器人启动脚本
echo "🚀 正在启动 AI 智能聊天助手..."
echo ""

# 检查 Python 版本
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ 错误：未找到 Python，请先安装 Python 3.x"
    exit 1
fi

echo "✅ 使用 Python: $PYTHON_CMD"
echo ""

# 检查依赖
echo "📦 检查依赖包..."
$PYTHON_CMD -c "import openai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  未安装 openai 库，正在安装..."
    $PYTHON_CMD -m pip install openai --quiet
    echo "✅ openai 库安装完成"
else
    echo "✅ openai 库已安装"
fi

echo ""
echo "=" | tr -d '\n' && printf '=%.0s' {1..60} && echo ""
echo "🤖 AI 智能聊天助手 - 多模型集成系统"
echo "=" | tr -d '\n' && printf '=%.0s' {1..60} && echo ""
echo ""

# 运行主程序
$PYTHON_CMD aichat.py

echo ""
echo "✨ 程序执行完毕！"
