#!/bin/bash

# 金融AI实时预测系统 - 快速启动脚本

echo "🚀 金融AI实时预测系统启动脚本"
echo "================================"
echo ""

# 检查 Python 版本
echo "📌 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python 3，请先安装 Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"
echo ""

# 检查 Node.js 版本
echo "📌 检查 Node.js 环境..."
if ! command -v node &> /dev/null; then
    echo "❌ 错误：未找到 Node.js，请先安装 Node.js 14+"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "✅ Node.js $NODE_VERSION"
echo ""

# 启动后端
echo "🔧 启动后端 WebSocket 服务器..."
cd backend || exit 1

if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

echo "⚙️ 激活虚拟环境..."
source venv/bin/activate

echo "📥 检查依赖..."
pip install -q -r requirements.txt

echo "🚀 启动后端服务器..."
python server.py &
BACKEND_PID=$!
cd ..

echo "✅ 后端已启动 (PID: $BACKEND_PID)"
echo ""

# 等待后端启动
sleep 2

# 启动前端
echo "🎨 启动前端 React 应用..."
cd frontend || exit 1

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

echo "🚀 启动前端开发服务器..."
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ 前端已启动 (PID: $FRONTEND_PID)"
echo ""
echo "✨ 系统启动完成！"
echo "==================="
echo "📊 访问地址：http://localhost:3000"
echo "🔌 WebSocket: ws://localhost:8080"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待中断信号
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '👋 系统已停止'; exit" INT
