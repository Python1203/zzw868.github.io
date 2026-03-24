/**
 * Binance WebSocket 自定义 Hook
 * 用于获取加密货币实时价格数据
 * 
 * @param {string[]} symbols - 交易对列表，例如 ['btcusdt', 'ethusdt']
 * @returns {Object} 实时价格数据
 * 
 * 使用示例:
 * const data = useBinanceWS(['btcusdt', 'ethusdt']);
 * // data.btcusdt = { price: '45230.50', change: '2.35', high: '46000', low: '44500' }
 */

import { useState, useEffect, useRef } from 'react';

export const useBinanceWS = (symbols = ['btcusdt']) => {
  const [data, setData] = useState({});
  const ws = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectTimeout = useRef(null);

  useEffect(() => {
    let isMounted = true;
    
    const connectWebSocket = () => {
      try {
        // 构建 WebSocket URL
        const streams = symbols.map(s => `${s.toLowerCase()}@ticker`).join('/');
        const wsUrl = `wss://stream.binance.com:9443/ws/${streams}`;
        
        console.log(`🔌 正在连接 Binance WebSocket: ${wsUrl}`);
        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
          console.log('✅ Binance WebSocket 已连接');
          reconnectAttempts.current = 0; // 重置重连计数
        };

        ws.current.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            const { stream, data: rawData } = message;
            const symbol = stream.split('@')[0].toUpperCase();
            
            if (isMounted) {
              setData(prev => ({
                ...prev,
                [symbol]: {
                  price: parseFloat(rawData.c).toFixed(2),
                  change: parseFloat(rawData.P).toFixed(2), // 24h 涨跌幅百分比
                  high: parseFloat(rawData.h).toFixed(2),
                  low: parseFloat(rawData.l).toFixed(2),
                  volume: parseFloat(rawData.v).toFixed(2),
                  timestamp: rawData.T
                }
              }));
            }
          } catch (error) {
            console.error('❌ 解析 Binance 数据失败:', error);
          }
        };

        ws.current.onerror = (error) => {
          console.error('❌ Binance WebSocket 错误:', error);
        };

        ws.current.onclose = () => {
          console.warn('⚠️ Binance WebSocket 断开连接');
          
          // 自动重连机制
          if (isMounted && reconnectAttempts.current < maxReconnectAttempts) {
            reconnectAttempts.current += 1;
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
            
            console.log(`🔄 ${delay/1000}秒后尝试第${reconnectAttempts.current}次重连...`);
            
            reconnectTimeout.current = setTimeout(() => {
              connectWebSocket();
            }, delay);
          } else if (reconnectAttempts.current >= maxReconnectAttempts) {
            console.error('❌ 达到最大重连次数，停止重连');
          }
        };

      } catch (error) {
        console.error('❌ 创建 Binance WebSocket 失败:', error);
      }
    };

    // 启动连接
    connectWebSocket();

    // 清理函数
    return () => {
      isMounted = false;
      
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
      
      if (ws.current) {
        ws.current.close();
        ws.current = null;
      }
      
      console.log('🔌 Binance WebSocket 连接已清理');
    };
  }, [symbols.join(',')]);

  return data;
};

// 辅助 Hook：获取单个币种数据
export const useSingleCrypto = (symbol) => {
  const data = useBinanceWS([symbol]);
  return data[symbol?.toUpperCase()] || null;
};

// 辅助 Hook：获取多个币种数据并排序
export const useCryptoPortfolio = (symbols) => {
  const data = useBinanceWS(symbols);
  
  const portfolio = Object.entries(data).map(([symbol, info]) => ({
    symbol,
    ...info,
    priceChangeColor: parseFloat(info.change) >= 0 ? '#52c41a' : '#ff4d4f'
  }));
  
  return portfolio.sort((a, b) => {
    // 按持有金额或交易量排序（可扩展）
    return parseFloat(b.volume) - parseFloat(a.volume);
  });
};
