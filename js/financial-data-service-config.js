/**
 * 金融数据 API 配置示例 v2.0
 * 
 * 使用说明：
 * 1. 复制此文件并重命名为 financial-data-service-config.js
 * 2. 填入您的真实 API Token/Key
 * 3. 在 financial-data-service.js 中引用此配置文件
 * 
 * 注意：此文件包含敏感信息，请勿提交到 Git 仓库！
 */

// ==================== Finnhub 配置（美股/全球市场）====================

const FINNHUB_CONFIG = {
  // 从 finnhub.io 获取的 API Token
  // 免费版每月 60 次调用，实时 WebSocket 数据
  token: 'd6rihfpr01qr194ms4ngd6rihfpr01qr194ms4o0', // 您提供的 Token
  
  // WebSocket 地址
  wsUrl: 'wss://ws.finnhub.io?token=d6rihfpr01qr194ms4ngd6rihfpr01qr194ms4o0',
  
  // 默认订阅的美股标的
  symbols: [
    'AAPL',     // 苹果公司
    'TSLA',     // 特斯拉
    'GOOGL',    // 谷歌
    'MSFT',     // 微软
    'AMZN'      // 亚马逊
  ],
  
  // 重连间隔（毫秒）
  reconnectDelay: 3000,
  
  // 心跳检测间隔（毫秒）
  heartbeatInterval: 30000
};

// ==================== Binance 配置（加密货币）====================

const BINANCE_CONFIG = {
  // API 基础地址
  baseUrl: 'https://api.binance.com',
  
  // 缓存超时时间（毫秒）
  priceCacheTimeout: 3000,  // 价格缓存 3 秒
  klineCacheTimeout: 5000,  // K 线缓存 5 秒
  
  // 默认市场
  defaultSymbol: 'BTCUSDT',
  
  // 支持的加密货币交易对
  supportedSymbols: [
    'BTCUSDT',  // 比特币
    'ETHUSDT',  // 以太坊
    'BNBUSDT',  // 币安币
    'XRPUSDT',  // 瑞波币
    'ADAUSDT',  // 艾达币
    'SOLUSDT',  // 索拉纳
    'DOGEUSDT'  // 狗狗币
  ],
  
  // 默认时间周期
  defaultTimeframe: '1h',
  
  // 请求限制（每秒）
  rateLimit: 10
};

// ==================== iTick 配置 ====================

const ITICK_CONFIG = {
  // 从 itick.org 获取的 API Token
  token: 'YOUR_ITICK_TOKEN_HERE',
  
  // WebSocket 地址（根据套餐选择）
  wsUrl: 'wss://api.itick.org/ws', // 免费版
  // wsUrl: 'wss://pro.itick.org/ws', // 付费版
  
  // 默认订阅的标的
  symbols: [
    '000001.XSHE',  // 平安银行（深交所）
    '600000.XSHG',  // 浦发银行（上交所）
    // 可以添加更多...
  ],
  
  // 重连间隔（毫秒）
  reconnectDelay: 3000,
  
  // 心跳检测间隔（毫秒）
  heartbeatInterval: 30000
};

// ==================== 沧海数据配置 ====================

const TSANGHI_CONFIG = {
  // 从 tsanghi.com 获取的 API Key
  apiKey: 'YOUR_TSANGHI_KEY_HERE',
  
  // API 基础地址
  baseUrl: 'https://api.tsanghi.com',
  
  // 缓存超时时间（毫秒）
  cacheTimeout: 5000, // K 线数据缓存 5 秒
  
  // 价格缓存超时时间（毫秒）
  priceCacheTimeout: 3000, // 价格缓存 3 秒
  
  // 默认市场
  defaultSymbol: 'BTCUSDT',
  
  // 默认时间周期
  defaultTimeframe: '1h',
  
  // 请求限制（每秒）
  rateLimit: 10
};

// ==================== 导出配置 ====================

// 浏览器环境
if (typeof window !== 'undefined') {
  window.FINNHUB_CONFIG = FINNHUB_CONFIG;
  window.BINANCE_CONFIG = BINANCE_CONFIG;
  window.ITICK_CONFIG = ITICK_CONFIG;
  window.TSANGHI_CONFIG = TSANGHI_CONFIG;
}

// Node.js 环境
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    FINNHUB_CONFIG,
    BINANCE_CONFIG,
    ITICK_CONFIG,
    TSANGHI_CONFIG
  };
}
