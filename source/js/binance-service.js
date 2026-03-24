/**
 * ========================================
 * Binance WebSocket 实时数据服务
 * 用途：提供加密货币实时行情数据
 * API 文档：https://binance-docs.github.io/apidocs/spot/en/#websocket-market-streams
 * ========================================
 */

class BinanceService {
  constructor() {
    this.ws = null;
    this.listeners = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.subscribedSymbols = new Set();
    this.isConnected = false;
    this.baseURL = 'https://api.binance.com/api/v3';
  }

  /**
   * 连接到 Binance WebSocket
   * @param {string} symbol - 交易对（如：btcusdt）
   */
  connect(symbol) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('✅ Binance WebSocket 已连接');
      return;
    }

    try {
      const streamURL = `wss://stream.binance.com:9443/ws/${symbol.toLowerCase()}@trade`;
      console.log('🔌 正在连接 Binance WebSocket:', streamURL);
      
      this.ws = new WebSocket(streamURL);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.subscribedSymbols.add(symbol);
        console.log(`✅ Binance WebSocket 连接成功 - ${symbol.toUpperCase()}`);
        
        // 通知所有监听器
        this.notifyListeners({ 
          type: 'connected',
          symbol: symbol.toUpperCase()
        });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data, symbol);
        } catch (error) {
          console.error('❌ 解析 Binance 消息失败:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ Binance WebSocket 错误:', error);
        this.notifyListeners({ 
          type: 'error', 
          error: 'WebSocket 连接错误' 
        });
      };

      this.ws.onclose = (event) => {
        this.isConnected = false;
        console.warn('⚠️ Binance WebSocket 关闭:', event.code, event.reason);
        this.notifyListeners({ 
          type: 'disconnected',
          code: event.code,
          reason: event.reason
        });
        
        // 自动重连
        if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect(symbol);
        }
      };

    } catch (error) {
      console.error('❌ 创建 Binance WebSocket 失败:', error);
      this.notifyListeners({ 
        type: 'error', 
        error: error.message 
      });
    }
  }

  /**
   * 处理接收到的消息
   */
  handleMessage(data, symbol) {
    if (data.e === 'trade') {
      // 实时成交数据
      const tickData = {
        type: 'trade',
        symbol: data.s,
        price: parseFloat(data.p),
        quantity: parseFloat(data.q),
        timestamp: data.T,
        buyerMaker: data.m // true 表示买单
      };
      this.notifyListeners(tickData);
    }
  }

  /**
   * 获取 REST API 数据（24 小时价格统计）
   * @param {string} symbol - 交易对（如：BTCUSDT）
   */
  async get24hrTicker(symbol) {
    try {
      const response = await fetch(`${this.baseURL}/ticker/24hr?symbol=${symbol.toUpperCase()}`);
      const data = await response.json();
      
      return {
        symbol: data.symbol,
        currentPrice: parseFloat(data.lastPrice),
        priceChange: parseFloat(data.priceChange),
        priceChangePercent: parseFloat(data.priceChangePercent),
        high24h: parseFloat(data.highPrice),
        low24h: parseFloat(data.lowPrice),
        volume24h: parseFloat(data.volume),
        quoteVolume24h: parseFloat(data.quoteVolume),
        timestamp: Date.now()
      };
    } catch (error) {
      console.error(`❌ 获取 ${symbol} 24 小时数据失败:`, error);
      throw error;
    }
  }

  /**
   * 获取 K 线数据
   * @param {string} symbol - 交易对
   * @param {string} interval - 时间间隔（1m, 5m, 1h, 4h, 1d 等）
   * @param {number} limit - 返回数量（默认 30）
   */
  async getKlineData(symbol, interval = '1h', limit = 30) {
    try {
      const response = await fetch(
        `${this.baseURL}/klines?symbol=${symbol.toUpperCase()}&interval=${interval}&limit=${limit}`
      );
      const data = await response.json();
      
      // 转换数据格式 [时间戳，开盘价，最高价，最低价，收盘价，成交量，...]
      return data.map(item => ({
        time: item[0],
        open: parseFloat(item[1]),
        high: parseFloat(item[3]),
        low: parseFloat(item[4]),
        close: parseFloat(item[5]),
        volume: parseFloat(item[6])
      }));
    } catch (error) {
      console.error(`❌ 获取 ${symbol} K 线数据失败:`, error);
      throw error;
    }
  }

  /**
   * 获取订单簿深度数据
   * @param {string} symbol - 交易对
   * @param {number} limit - 返回数量（5, 10, 20, 50, 100）
   */
  async getOrderBook(symbol, limit = 20) {
    try {
      const response = await fetch(
        `${this.baseURL}/depth?symbol=${symbol.toUpperCase()}&limit=${limit}`
      );
      const data = await response.json();
      
      return {
        bids: data.bids.map(bid => [parseFloat(bid[0]), parseFloat(bid[1])]), // [价格，数量]
        asks: data.asks.map(ask => [parseFloat(ask[0]), parseFloat(ask[1])])
      };
    } catch (error) {
      console.error(`❌ 获取 ${symbol} 订单簿失败:`, error);
      throw error;
    }
  }

  /**
   * 安排重新连接
   */
  scheduleReconnect(symbol) {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`🔄 计划第 ${this.reconnectAttempts} 次重连 ${symbol}，延迟 ${delay}ms`);
    
    setTimeout(() => {
      console.log(`🔄 开始重连 ${symbol}...`);
      this.connect(symbol);
    }, delay);
  }

  /**
   * 添加数据监听器
   */
  addListener(callback) {
    this.listeners.push(callback);
    
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  /**
   * 通知所有监听器
   */
  notifyListeners(data) {
    this.listeners.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error('❌ Binance 监听器回调错误:', error);
      }
    });
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
      this.listeners = [];
      this.subscribedSymbols.clear();
      
      console.log('🔌 Binance WebSocket 已断开');
    }
  }

  /**
   * 获取连接状态
   */
  getStatus() {
    return {
      connected: this.isConnected,
      subscribedSymbols: Array.from(this.subscribedSymbols),
      reconnectAttempts: this.reconnectAttempts
    };
  }
}

// 自动初始化
(function initBinanceService() {
  window.binanceService = new BinanceService();
  console.log('✅ Binance 服务已初始化');
})();
