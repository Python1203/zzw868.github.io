/**
 * 金融数据服务层 v2.0
 * 支持多种数据源：
 * - iTick WebSocket（股票）
 * - Finnhub WebSocket（美股/全球市场）
 * - 沧海数据 REST API（加密货币）
 * - Binance API（加密货币）
 * 
 * 配置说明：
 * 1. 复制 financial-data-service-config.example.js
 * 2. 重命名为 financial-data-service-config.js
 * 3. 填入您的真实 API Token/Key
 * 4. 取消下方注释引入配置文件
 */

// 引入配置文件（已创建并配置）
if (typeof window !== 'undefined' && document) {
  const script = document.createElement('script');
  script.src = '/js/financial-data-service-config.js';
  document.head.appendChild(script);
}

// ==================== iTick WebSocket 服务（股票数据）====================

class ITickWebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectTimer = null;
    this.listeners = [];
    this.isConnected = false;
    
    // 优先使用配置文件，否则使用默认值
    const config = window.ITICK_CONFIG || {};
    this.token = config.token || 'YOUR_ITICK_TOKEN';
    this.symbols = config.symbols || ['000001.XSHE', '600000.XSHG'];
    this.wsUrl = config.wsUrl || 'wss://api.itick.org/ws';
    this.reconnectDelay = config.reconnectDelay || 3000;
  }

  /**
   * 连接 WebSocket
   */
  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('✅ iTick WebSocket 已连接');
      return;
    }

    try {
      // iTick WebSocket 地址
      const wsUrl = `${this.wsUrl}?token=${this.token}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
        console.log('✅ iTick WebSocket 连接成功');
        
        // 订阅行情
        this.subscribe(this.symbols);
        
        // 通知监听器
        this.listeners.forEach(cb => cb({ type: 'connected' }));
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📊 收到 iTick 数据:', data);
          
          // 转换为统一格式
          const formattedData = this.formatTickData(data);
          this.listeners.forEach(cb => cb(formattedData));
        } catch (error) {
          console.error('❌ 解析 iTick 数据失败:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ iTick WebSocket 错误:', error);
        this.isConnected = false;
        this.listeners.forEach(cb => cb({ type: 'error', error }));
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        console.log('⚠️ iTick WebSocket 连接关闭，尝试重连...');
        
        // 自动重连
        if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
        this.reconnectTimer = setTimeout(() => this.connect(), this.reconnectDelay);
        
        this.listeners.forEach(cb => cb({ type: 'disconnected' }));
      };

    } catch (error) {
      console.error('❌ 创建 iTick WebSocket 失败:', error);
      this.isConnected = false;
    }
  }

  /**
   * 订阅标的
   */
  subscribe(symbols) {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ WebSocket 未连接，无法订阅');
      return;
    }

    const subscribeMsg = {
      cmd: 'subscribe',
      body: {
        symbols: symbols.join(',')
      }
    };

    this.ws.send(JSON.stringify(subscribeMsg));
    console.log('📡 已订阅:', symbols);
  }

  /**
   * 取消订阅
   */
  unsubscribe(symbols) {
    if (this.ws?.readyState !== WebSocket.OPEN) return;

    const unsubscribeMsg = {
      cmd: 'unsubscribe',
      body: {
        symbols: symbols.join(',')
      }
    };

    this.ws.send(JSON.stringify(unsubscribeMsg));
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
  }

  /**
   * 添加数据监听器
   */
  addListener(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  /**
   * 格式化 iTick 数据为统一格式
   */
  formatTickData(tickData) {
    // 根据实际 iTick 返回格式调整
    return {
      symbol: tickData.symbol || 'unknown',
      price: tickData.last || tickData.price || 0,
      open: tickData.open || 0,
      high: tickData.high || 0,
      low: tickData.low || 0,
      close: tickData.last || 0,
      volume: tickData.volume || 0,
      timestamp: tickData.time || Date.now(),
      change: tickData.change || 0,
      changePercent: tickData.pct || 0
    };
  }
}

// ==================== 沧海数据 REST API 服务（加密货币）====================

class TsanghiRestService {
  constructor() {
    // 优先使用配置文件，否则使用默认值
    const config = window.TSANGHI_CONFIG || {};
    this.baseUrl = config.baseUrl || 'https://api.tsanghi.com';
    this.apiKey = config.apiKey || 'YOUR_TSANGHI_KEY';
    this.cacheTimeout = config.cacheTimeout || 5000;
    this.priceCacheTimeout = config.priceCacheTimeout || 3000;
    
    this.cache = new Map();
  }

  /**
   * 获取 K 线数据
   */
  async getKlineData(symbol = 'BTCUSDT', timeframe = '1h', limit = 100) {
    try {
      const cacheKey = `kline_${symbol}_${timeframe}`;
      
      // 检查缓存
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey);
        if (Date.now() - cached.timestamp < this.cacheTimeout) {
          console.log('💾 使用缓存数据:', cacheKey);
          return cached.data;
        }
      }

      // 请求 API
      const url = `${this.baseUrl}/crypto/kline?symbol=${symbol}&timeframe=${timeframe}&limit=${limit}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP 错误：${response.status}`);
      }

      const data = await response.json();
      
      // 缓存数据
      this.cache.set(cacheKey, {
        data: this.formatKlineData(data),
        timestamp: Date.now()
      });

      console.log('📊 获取沧海数据 K 线:', symbol);
      return this.formatKlineData(data);

    } catch (error) {
      console.error('❌ 获取沧海数据失败:', error);
      // 降级到模拟数据
      return this.generateMockKlineData(symbol);
    }
  }

  /**
   * 获取实时价格
   */
  async getPrice(symbol = 'BTCUSDT') {
    try {
      const cacheKey = `price_${symbol}`;
      
      // 检查缓存
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey);
        if (Date.now() - cached.timestamp < this.priceCacheTimeout) { // 3 秒缓存
          return cached.data;
        }
      }

      const url = `${this.baseUrl}/crypto/price?symbol=${symbol}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        }
      });

      const data = await response.json();
      const priceData = {
        symbol: symbol,
        price: data.price || 0,
        change24h: data.change24h || 0,
        high24h: data.high24h || 0,
        low24h: data.low24h || 0,
        volume24h: data.volume24h || 0
      };

      this.cache.set(cacheKey, {
        data: priceData,
        timestamp: Date.now()
      });

      return priceData;

    } catch (error) {
      console.error('❌ 获取价格失败:', error);
      return this.generateMockPriceData(symbol);
    }
  }

  /**
   * 获取市场深度
   */
  async getOrderBook(symbol = 'BTCUSDT', limit = 20) {
    try {
      const url = `${this.baseUrl}/crypto/orderbook?symbol=${symbol}&limit=${limit}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        }
      });

      const data = await response.json();
      return {
        bids: data.bids || [],
        asks: data.asks || []
      };

    } catch (error) {
      console.error('❌ 获取订单簿失败:', error);
      return { bids: [], asks: [] };
    }
  }

  /**
   * 格式化 K 线数据
   */
  formatKlineData(apiData) {
    // 根据实际 API 返回格式调整
    return apiData.map(item => [
      item.time,      // 时间戳
      item.open,      // 开盘价
      item.close,     // 收盘价
      item.low,       // 最低价
      item.high,      // 最高价
      item.volume     // 成交量
    ]);
  }

  /**
   * 生成模拟 K 线数据（降级方案）
   */
  generateMockKlineData(symbol = 'BTCUSDT') {
    const basePrice = symbol.includes('BTC') ? 50000 : 
                     symbol.includes('ETH') ? 3000 : 100;
    
    const data = [];
    let price = basePrice;
    const now = Date.now();
    
    for (let i = 30; i >= 0; i--) {
      const time = now - i * 3600000;
      const open = price;
      const close = price + (Math.random() - 0.5) * 1000;
      const high = Math.max(open, close) + Math.random() * 500;
      const low = Math.min(open, close) - Math.random() * 500;
      const volume = Math.random() * 100 + 50;
      
      data.push([time, open, close, low, high, volume]);
      price = close;
    }
    
    return data;
  }

  /**
   * 生成模拟价格数据（降级方案）
   */
  generateMockPriceData(symbol = 'BTCUSDT') {
    const basePrice = symbol.includes('BTC') ? 50000 : 
                     symbol.includes('ETH') ? 3000 : 100;
    
    return {
      symbol: symbol,
      price: basePrice + (Math.random() - 0.5) * 100,
      change24h: (Math.random() - 0.5) * 10,
      high24h: basePrice * 1.05,
      low24h: basePrice * 0.95,
      volume24h: Math.random() * 1000000 + 500000
    };
  }
}

// ==================== Finnhub WebSocket 服务（美股/全球市场）====================

class FinnhubWebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectTimer = null;
    this.listeners = [];
    this.isConnected = false;
    
    // 优先使用配置文件，否则使用默认值
    const config = window.FINNHUB_CONFIG || {};
    this.token = config.token || 'YOUR_FINNHUB_TOKEN';
    this.symbols = config.symbols || ['AAPL', 'TSLA', 'GOOGL'];
    this.wsUrl = config.wsUrl || `wss://ws.finnhub.io?token=${this.token}`;
    this.reconnectDelay = config.reconnectDelay || 3000;
  }

  /**
   * 连接 WebSocket
   */
  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('✅ Finnhub WebSocket 已连接');
      return;
    }

    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
        console.log('✅ Finnhub WebSocket 连接成功');
        
        // 订阅行情
        this.subscribe(this.symbols);
        
        // 通知监听器
        this.listeners.forEach(cb => cb({ type: 'connected' }));
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📊 收到 Finnhub 数据:', data);
          
          // 转换为统一格式
          if (data.type === 'trade') {
            const formattedData = this.formatFinnhubData(data);
            this.listeners.forEach(cb => cb(formattedData));
          }
        } catch (error) {
          console.error('❌ 解析 Finnhub 数据失败:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ Finnhub WebSocket 错误:', error);
        this.isConnected = false;
        this.listeners.forEach(cb => cb({ type: 'error', error }));
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        console.log('⚠️ Finnhub WebSocket 连接关闭，尝试重连...');
        
        // 自动重连
        if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
        this.reconnectTimer = setTimeout(() => this.connect(), this.reconnectDelay);
        
        this.listeners.forEach(cb => cb({ type: 'disconnected' }));
      };

    } catch (error) {
      console.error('❌ 创建 Finnhub WebSocket 失败:', error);
      this.isConnected = false;
    }
  }

  /**
   * 订阅标的
   */
  subscribe(symbols) {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ WebSocket 未连接，无法订阅');
      return;
    }

    symbols.forEach(symbol => {
      const subscribeMsg = {
        type: 'subscribe',
        symbol: symbol
      };
      this.ws.send(JSON.stringify(subscribeMsg));
      console.log('📡 已订阅 Finnhub:', symbol);
    });
  }

  /**
   * 取消订阅
   */
  unsubscribe(symbols) {
    if (this.ws?.readyState !== WebSocket.OPEN) return;

    symbols.forEach(symbol => {
      const unsubscribeMsg = {
        type: 'unsubscribe',
        symbol: symbol
      };
      this.ws.send(JSON.stringify(unsubscribeMsg));
    });
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
  }

  /**
   * 添加数据监听器
   */
  addListener(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  /**
   * 格式化 Finnhub 数据为统一格式
   */
  formatFinnhubData(tradeData) {
    // Finnhub trade 数据格式：{"type":"trade","symbol":"AAPL","data":[{"p":150.5,"v":100,"t":1234567890}]}
    if (!tradeData.data || tradeData.data.length === 0) return null;
    
    const latestTrade = tradeData.data[tradeData.data.length - 1];
    
    return {
      symbol: tradeData.symbol,
      price: latestTrade.p || 0,           // 价格
      volume: latestTrade.v || 0,          // 成交量
      timestamp: latestTrade.t || Date.now(), // 时间戳
      change: 0,                           // Finnhub 不提供涨跌幅，需要计算
      changePercent: 0
    };
  }
}

// ==================== Binance API 服务（加密货币）====================

class BinanceRestService {
  constructor() {
    this.baseUrl = 'https://api.binance.com'; // Binance API 基础地址
    this.cache = new Map();
    this.cacheTimeout = 3000; // 3 秒缓存
  }

  /**
   * 获取实时价格
   */
  async getPrice(symbol = 'BTCUSDT') {
    try {
      const cacheKey = `price_${symbol}`;
      
      // 检查缓存
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey);
        if (Date.now() - cached.timestamp < this.cacheTimeout) {
          return cached.data;
        }
      }

      // 请求 Binance API
      const url = `${this.baseUrl}/api/v3/ticker/price?symbol=${symbol}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP 错误：${response.status}`);
      }

      const data = await response.json();
      const priceData = {
        symbol: data.symbol,
        price: parseFloat(data.price),
        timestamp: Date.now()
      };

      // 缓存数据
      this.cache.set(cacheKey, {
        data: priceData,
        timestamp: Date.now()
      });

      console.log('💰 Binance 价格:', symbol, priceData.price);
      return priceData;

    } catch (error) {
      console.error('❌ 获取 Binance 价格失败:', error);
      // 降级到模拟数据
      return this.generateMockPriceData(symbol);
    }
  }

  /**
   * 获取 24 小时行情
   */
  async get24hTicker(symbol = 'BTCUSDT') {
    try {
      const url = `${this.baseUrl}/api/v3/ticker/24hr?symbol=${symbol}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP 错误：${response.status}`);
      }

      const data = await response.json();
      return {
        symbol: data.symbol,
        price: parseFloat(data.lastPrice),
        changePercent: parseFloat(data.priceChangePercent),
        high24h: parseFloat(data.highPrice),
        low24h: parseFloat(data.lowPrice),
        volume24h: parseFloat(data.volume),
        timestamp: Date.now()
      };

    } catch (error) {
      console.error('❌ 获取 Binance 24h 行情失败:', error);
      return this.generateMock24hData(symbol);
    }
  }

  /**
   * 获取 K 线数据
   */
  async getKlineData(symbol = 'BTCUSDT', interval = '1h', limit = 30) {
    try {
      const cacheKey = `kline_${symbol}_${interval}`;
      
      // 检查缓存
      if (this.cache.has(cacheKey)) {
        const cached = this.cache.get(cacheKey);
        if (Date.now() - cached.timestamp < 5000) { // 5 秒缓存
          return cached.data;
        }
      }

      const url = `${this.baseUrl}/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP 错误：${response.status}`);
      }

      const data = await response.json();
      
      // Binance K 线格式：[时间戳，开盘价，最高价，最低价，收盘价，成交量，...]
      const klineData = data.map(item => [
        item[0],                    // 时间戳
        parseFloat(item[1]),        // 开盘价
        parseFloat(item[3]),        // 最低价
        parseFloat(item[2]),        // 最高价
        parseFloat(item[4]),        // 收盘价
        parseFloat(item[5])         // 成交量
      ]);

      // 缓存数据
      this.cache.set(cacheKey, {
        data: klineData,
        timestamp: Date.now()
      });

      console.log('📊 Binance K 线:', symbol, klineData.length, '条');
      return klineData;

    } catch (error) {
      console.error('❌ 获取 Binance K 线失败:', error);
      return this.generateMockKlineData(symbol);
    }
  }

  /**
   * 生成模拟价格数据（降级方案）
   */
  generateMockPriceData(symbol = 'BTCUSDT') {
    const basePrice = symbol.includes('BTC') ? 50000 : 
                     symbol.includes('ETH') ? 3000 : 100;
    
    return {
      symbol: symbol,
      price: basePrice + (Math.random() - 0.5) * 100,
      timestamp: Date.now()
    };
  }

  /**
   * 生成模拟 24h 数据（降级方案）
   */
  generateMock24hData(symbol = 'BTCUSDT') {
    const basePrice = symbol.includes('BTC') ? 50000 : 
                     symbol.includes('ETH') ? 3000 : 100;
    
    return {
      symbol: symbol,
      price: basePrice,
      changePercent: (Math.random() - 0.5) * 10,
      high24h: basePrice * 1.05,
      low24h: basePrice * 0.95,
      volume24h: Math.random() * 1000000 + 500000
    };
  }

  /**
   * 生成模拟 K 线数据（降级方案）
   */
  generateMockKlineData(symbol = 'BTCUSDT') {
    const basePrice = symbol.includes('BTC') ? 50000 : 
                     symbol.includes('ETH') ? 3000 : 100;
    
    const data = [];
    let price = basePrice;
    const now = Date.now();
    
    for (let i = 30; i >= 0; i--) {
      const time = now - i * 3600000;
      const open = price;
      const close = price + (Math.random() - 0.5) * 1000;
      const high = Math.max(open, close) + Math.random() * 500;
      const low = Math.min(open, close) - Math.random() * 500;
      const volume = Math.random() * 100 + 50;
      
      data.push([time, open, low, high, close, volume]);
      price = close;
    }
    
    return data;
  }
}

// ==================== 导出单例 ====================

const iTickService = new ITickWebSocketService();
const finnhubService = new FinnhubWebSocketService();
const tsanghiService = new TsanghiRestService();
const binanceService = new BinanceRestService();

// 全局导出（浏览器环境）
if (typeof window !== 'undefined') {
  window.iTickService = iTickService;
  window.finnhubService = finnhubService;
  window.tsanghiService = tsanghiService;
  window.binanceService = binanceService;
}

// 注释掉 ES6 export，避免浏览器报错
// export { iTickService, finnhubService, tsanghiService, binanceService };
