/**
 * ========================================
 * Finnhub WebSocket 实时数据服务
 * 用途：提供美股实时交易数据
 * API 文档：https://finnhub.io/docs/api/websocket
 * ========================================
 */

class FinnhubService {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.ws = null;
    this.listeners = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000; // 3 秒后重试
    this.subscribedSymbols = new Set();
    this.isConnected = false;
  }

  /**
   * 连接到 Finnhub WebSocket
   */
  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('✅ Finnhub WebSocket 已连接');
      return;
    }

    try {
      console.log('🔌 正在连接 Finnhub WebSocket...');
      this.ws = new WebSocket(`wss://ws.finnhub.io?token=${this.apiKey}`);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        console.log('✅ Finnhub WebSocket 连接成功');
        
        // 通知所有监听器
        this.notifyListeners({ type: 'connected' });
        
        // 重新订阅之前关注的股票
        this.subscribedSymbols.forEach(symbol => {
          this.subscribe(symbol);
        });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('❌ 解析 Finnhub 消息失败:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ Finnhub WebSocket 错误:', error);
        console.warn('⚠️ 可能原因：1) API Key 无效 2) 网络问题 3) Finnhub 服务限制');
        this.notifyListeners({ 
          type: 'error', 
          error: 'WebSocket 连接错误' 
        });
        
        // 立即标记为失败，触发降级
        this.isConnected = false;
      };

      this.ws.onclose = (event) => {
        this.isConnected = false;
        console.warn('⚠️ Finnhub WebSocket 关闭:', event.code, event.reason || '');
        
        // 根据关闭代码判断是否重连
        const shouldReconnect = !event.wasClean && 
                                this.reconnectAttempts < this.maxReconnectAttempts &&
                                event.code !== 1000; // 1000 表示正常关闭
        
        if (shouldReconnect) {
          console.log(`🔄 ${this.reconnectDelay}ms 后尝试第 ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts} 次重连...`);
          setTimeout(() => {
            console.log('🔄 开始重连 Finnhub...');
            this.connect();
          }, this.reconnectDelay);
        } else {
          console.log('ℹ️ Finnhub WebSocket 已正常关闭，不再重连');
        }
        
        this.notifyListeners({ 
          type: 'disconnected',
          code: event.code,
          reason: event.reason || ''
        });
      };

    } catch (error) {
      console.error('❌ 创建 Finnhub WebSocket 失败:', error);
      this.notifyListeners({ 
        type: 'error', 
        error: error.message 
      });
    }
  }

  /**
   * 处理接收到的消息
   */
  handleMessage(data) {
    if (data.type === 'trade') {
      // 实时交易数据
      data.data.forEach(trade => {
        const tickData = {
          type: 'trade',
          symbol: trade.s,
          price: trade.p,
          volume: trade.v,
          timestamp: trade.t,
          changePercent: trade.chgp || 0
        };
        this.notifyListeners(tickData);
      });
    } else if (data.type === 'quote') {
      // 报价更新
      data.data.forEach(quote => {
        const tickData = {
          type: 'quote',
          symbol: quote.s,
          currentPrice: quote.c,
          high: quote.h,
          low: quote.l,
          open: quote.o,
          previousClose: quote.pc,
          timestamp: Date.now()
        };
        this.notifyListeners(tickData);
      });
    }
  }

  /**
   * 订阅股票行情
   * @param {string} symbol - 股票代码（如：AAPL, TSLA）
   */
  subscribe(symbol) {
    if (!this.isConnected || this.ws?.readyState !== WebSocket.OPEN) {
      console.warn(`⚠️ 无法订阅 ${symbol}：WebSocket 未连接`);
      return;
    }

    try {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        symbol: symbol.toUpperCase()
      }));
      
      this.subscribedSymbols.add(symbol.toUpperCase());
      console.log(`📡 已订阅股票：${symbol.toUpperCase()}`);
    } catch (error) {
      console.error(`❌ 订阅 ${symbol} 失败:`, error);
    }
  }

  /**
   * 取消订阅股票
   */
  unsubscribe(symbol) {
    if (!this.isConnected || this.ws?.readyState !== WebSocket.OPEN) {
      return;
    }

    try {
      this.ws.send(JSON.stringify({
        type: 'unsubscribe',
        symbol: symbol.toUpperCase()
      }));
      
      this.subscribedSymbols.delete(symbol.toUpperCase());
      console.log(`📡 已取消订阅：${symbol.toUpperCase()}`);
    } catch (error) {
      console.error(`❌ 取消订阅 ${symbol} 失败:`, error);
    }
  }

  /**
   * 安排重新连接
   */
  scheduleReconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // 指数退避
    
    console.log(`🔄 计划第 ${this.reconnectAttempts} 次重连，延迟 ${delay}ms`);
    
    setTimeout(() => {
      console.log('🔄 开始重连 Finnhub...');
      this.connect();
    }, delay);
  }

  /**
   * 添加数据监听器
   * @param {Function} callback - 回调函数，接收 tickData 对象
   * @returns {Function} - 移除监听器的函数
   */
  addListener(callback) {
    this.listeners.push(callback);
    
    // 返回移除函数
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
        console.error('❌ Finnhub 监听器回调错误:', error);
      }
    });
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.ws) {
      // 取消所有订阅
      this.subscribedSymbols.forEach(symbol => {
        this.unsubscribe(symbol);
      });
      
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
      this.listeners = [];
      this.subscribedSymbols.clear();
      
      console.log('🔌 Finnhub WebSocket 已断开');
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

// 自动初始化（如果存在 API Key）
(function initFinnhubService() {
  // 从环境变量或配置中读取 API Key
  const apiKey = window.FINNHUB_API_KEY || localStorage.getItem('finnhub_api_key');
  
  if (apiKey) {
    window.finnhubService = new FinnhubService(apiKey);
    console.log('✅ Finnhub 服务已初始化');
  } else {
    console.warn('⚠️ 未找到 Finnhub API Key，请在 .env 文件中设置 FINNHUB_API_KEY');
  }
})();
