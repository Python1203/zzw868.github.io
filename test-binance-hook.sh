#!/bin/bash

# 测试 Binance WebSocket Hook
echo "🚀 启动 Binance WebSocket Hook 测试..."
echo ""

# 检查文件是否存在
if [ ! -f ".deploy_git/js/useBinanceWS.js" ]; then
    echo "❌ useBinanceWS.js 不存在!"
    exit 1
fi

if [ ! -f ".deploy_git/components/crypto-price-widget.html" ]; then
    echo "❌ crypto-price-widget.html 不存在!"
    exit 1
fi

echo "✅ 文件检查通过"
echo ""
echo "📁 已创建的文件:"
echo "   - source/js/useBinanceWS.js (可复用 Hook)"
echo "   - source/components/crypto-price-widget.html (演示组件)"
echo "   - source/js/README_BINANCE_HOOK.md (使用文档)"
echo ""
echo "🌐 测试步骤:"
echo "   1. 在浏览器中打开：http://localhost:4000/components/crypto-price-widget.html"
echo "   2. 或者部署到 GitHub Pages 后访问"
echo ""
echo "💡 提示："
echo "   - Hook 会自动连接 Binance WebSocket"
echo "   - 支持 BTC、ETH、BNB 等主流币种"
echo "   - 包含自动重连机制"
echo "   - 组件卸载时自动清理连接"
echo ""
echo "🎯 使用示例:"
echo '   import { useBinanceWS } from "./js/useBinanceWS";'
echo '   const data = useBinanceWS(["btcusdt", "ethusdt"]);'
echo ""
echo "✨ 完成！"
