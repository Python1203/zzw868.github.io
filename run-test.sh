#!/bin/bash

# 实时股票价格预测图表 - 测试运行脚本
# 用于快速启动测试环境

echo "🚀 启动实时股票价格预测图表测试..."
echo ""

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 未检测到 Node.js，请先安装 Node.js"
    exit 1
fi

echo "✅ Node.js 版本："
node --version
echo ""

# 检查 ws 包是否安装
if [ ! -d "node_modules/ws" ]; then
    echo "📦 正在安装 WebSocket 依赖..."
    npm install ws
    echo ""
fi

# 启动模拟服务器（后台运行）
echo "🔌 启动模拟 WebSocket 服务器..."
node mock-ws-server.js &
WS_PID=$!
echo "✅ WebSocket 服务器已启动 (PID: $WS_PID)"
echo ""

# 等待 2 秒让服务器完全启动
sleep 2

# 打开浏览器
echo "🌐 正在打开测试页面..."
echo ""
echo "=========================================="
echo "✨ 测试环境已就绪！"
echo "=========================================="
echo ""
echo "📊 测试页面：test-stock-chart.html"
echo "   - 在浏览器中打开此文件即可查看效果"
echo "   - 或使用本地服务器访问"
echo ""
echo "🎮 控制面板功能："
echo "   • 📊 开始模拟数据 - 自动生成实时价格"
echo "   • 📈 发送预测 - 手动发送单条预测"
echo "   • 🔌 断开连接 - 测试断线重连"
echo "   • 🗑️ 清空数据 - 重置图表"
echo ""
echo "💡 优化特性："
echo "   ✓ 连接状态可视化（绿/黄/灰/红）"
echo "   ✓ 自动重连机制（3 秒延迟）"
echo "   ✓ 错误处理和日志记录"
echo "   ✓ 性能优化（useCallback + 数据限制）"
echo "   ✓ 自定义 Tooltip 和货币格式化"
echo "   ✓ 响应式 UI 设计"
echo ""
echo "=========================================="
echo ""
echo "按 Ctrl+C 停止 WebSocket 服务器并退出"
echo ""

# 捕获退出信号
trap "kill $WS_PID 2>/dev/null; echo ''; echo '🛑 测试已结束'; exit" INT TERM EXIT

# 保持脚本运行
wait $WS_PID
