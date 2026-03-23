/**
 * 模拟 WebSocket 服务器 - 用于测试 RealTimeStockChart 组件
 * 
 * 使用方法：
 * 1. 安装 ws: npm install ws
 * 2. 运行：node mock-ws-server.js
 * 3. 打开 test-stock-chart.html 查看效果
 */

const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

let basePrice = 150 + Math.random() * 50;

console.log('🚀 模拟 WebSocket 服务器已启动');
console.log('📡 监听端口：ws://localhost:8080');
console.log('📊 初始价格：￥' + basePrice.toFixed(2));
console.log('按 Ctrl+C 停止服务\n');

wss.on('connection', (ws) => {
    console.log('✅ 客户端已连接');
    
    // 每秒发送预测数据
    const interval = setInterval(() => {
        // 随机价格波动
        basePrice = basePrice + (Math.random() - 0.5) * 3;
        basePrice = Math.max(50, Math.min(250, basePrice)); // 限制在 50-250 之间
        
        const prediction = {
            predictedPrice: Number(basePrice.toFixed(2)),
            predictedTrendProbability: Number(Math.random().toFixed(4)),
            timestamp: new Date().toISOString()
        };
        
        const message = {
            type: 'prediction',
            data: prediction
        };
        
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
            console.log(`📈 发送预测：￥${prediction.predictedPrice} | 涨价概率：${(prediction.predictedTrendProbability * 100).toFixed(1)}%`);
        }
    }, 2000);
    
    ws.on('close', () => {
        console.log('❌ 客户端已断开');
        clearInterval(interval);
    });
    
    ws.on('error', (error) => {
        console.error('❌ WebSocket 错误:', error.message);
    });
});

wss.on('error', (error) => {
    console.error('服务器错误:', error.message);
});

// 优雅退出
process.on('SIGINT', () => {
    console.log('\n🛑 正在关闭服务器...');
    wss.close(() => {
        console.log('服务器已关闭');
        process.exit(0);
    });
});
