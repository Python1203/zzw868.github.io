/**
 * 金融数据 API 配置指南
 * 
 * 本文件说明如何配置和使用真实金融数据源
 */

// ==================== iTick 配置（股票数据）====================

/**
 * 1. 注册 iTick 账号
 *    - 访问：https://www.itick.org/
 *    - 注册免费账号
 *    - 获取 API Token
 */

/**
 * 2. 配置 Token
 *    在 financial-data-service.js 中找到以下代码：
 *    
 *    this.token = 'YOUR_ITICK_TOKEN'; // 替换为您的实际 token
 *    
 *    将 YOUR_ITICK_TOKEN 替换为您从 iTick 获取的 Token
 */

/**
 * 3. 订阅标的配置
 *    iTick 使用以下格式：
 *    - A 股：股票代码。交易所后缀
 *      - 深交所：000001.XSHE（平安银行）
 *      - 上交所：600000.XSHG（浦发银行）
 *    - 港股：HK.股票代码（HK.00700 腾讯控股）
 *    - 美股：US.股票代码（US.AAPL 苹果）
 *    
 *    修改示例：
 *    this.symbols = ['000001.XSHE', '600000.XSHG']; // 默认标的
 *    
 *    可以添加更多标的：
 *    this.symbols = [
 *      '000001.XSHE',  // 平安银行
 *      '600000.XSHG',  // 浦发银行
 *      'HK.00700',     // 腾讯控股
 *      'US.AAPL'       // 苹果公司
 *    ];
 */

/**
 * 4. WebSocket 连接地址
 *    iTick WebSocket 地址可能因服务套餐而异，请参考官方文档：
 *    - 免费版：wss://api.itick.org/ws
 *    - 付费版：wss://pro.itick.org/ws
 */


// ==================== 沧海数据配置（加密货币）====================

/**
 * 1. 注册沧海数据账号
 *    - 访问：https://www.tsanghi.com/
 *    - 注册免费账号
 *    - 获取 API Key
 */

/**
 * 2. 配置 API Key
 *    在 financial-data-service.js 中找到以下代码：
 *    
 *    this.baseUrl = 'https://api.tsanghi.com'; // 沧海数据 API 地址
 *    this.apiKey = 'YOUR_TSANGHI_KEY'; // 从 tsanghi.com 获取
 *    
 *    将 YOUR_TSANGHI_KEY 替换为您从沧海数据获取的 Key
 */

/**
 * 3. API 端点说明
 *    沧海数据提供以下主要接口：
 *    
 *    a) K 线数据：
 *       GET /crypto/kline?symbol=BTCUSDT&timeframe=1h&limit=100
 *       
 *    b) 实时价格：
 *       GET /crypto/price?symbol=BTCUSDT
 *       
 *    c) 市场深度：
 *       GET /crypto/orderbook?symbol=BTCUSDT&limit=20
 *       
 *    d) 24 小时行情：
 *       GET /crypto/ticker/24h?symbol=BTCUSDT
 */

/**
 * 4. 支持的加密货币交易对
 *    - BTCUSDT: 比特币/USDT
 *    - ETHUSDT: 以太坊/USDT
 *    - LTCUSDT: 莱特币/USDT
 *    - XRPUSDT: 瑞波币/USDT
 *    - ADAUSDT: 艾达币/USDT
 *    
 *    可以在 crypto-dashboard-widget.html 中修改 markets 数组来自定义：
 *    
 *    const markets = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'XRPUSDT', 'ADAUSDT'];
 */


// ==================== 降级方案 ====================

/**
 * 当 API 不可用时的自动降级策略：
 * 
 * 1. 如果 iTick 或沧海数据连接失败，组件会自动切换到模拟数据模式
 * 2. 用户也可以手动切换回模拟数据模式
 * 3. 模拟数据保证演示和测试功能正常
 * 
 * 降级逻辑示例：
 * 
 * try {
 *   // 尝试连接真实数据源
 *   await tsanghiService.getKlineData('BTCUSDT');
 * } catch (error) {
 *   console.error('真实数据加载失败，降级到模拟数据');
 *   // 使用模拟数据
 *   generateMockKlineData();
 * }
 */


// ==================== 使用说明 ====================

/**
 * 使用步骤：
 * 
 * 1. 获取 API Key
 *    - iTick: https://www.itick.org/
 *    - 沧海数据：https://www.tsanghi.com/
 * 
 * 2. 配置 Token/Key
 *    - 打开 source/js/financial-data-service.js
 *    - 替换 YOUR_ITICK_TOKEN 和 YOUR_TSANGHI_KEY
 * 
 * 3. 重启 Hexo 服务器
 *    hexo clean && hexo generate
 *    hexo server
 * 
 * 4. 访问博客主页
 *    - 点击组件右上角的"切换真实数据"按钮
 *    - 观察实时数据更新
 * 
 * 5. 监控控制台日志
 *    - 打开浏览器开发者工具
 *    - 查看 Console 中的连接和数据日志
 */


// ==================== 常见问题 ====================

/**
 * Q1: 为什么切换真实数据后没有数据显示？
 * A: 检查以下几点：
 *    1. 是否正确配置了 Token/Key
 *    2. 网络连接是否正常
 *    3. 浏览器控制台是否有错误信息
 *    4. API 额度是否用完
 * 
 * Q2: 数据更新频率是多少？
 * A: 
 *    - iTick WebSocket: 实时推送（毫秒级）
 *    - 沧海数据 REST: 每 10 秒轮询一次
 * 
 * Q3: 免费额度是多少？
 * A: 
 *    - iTick: 基础免费版有连接数和频率限制
 *    - 沧海数据: 基础免费版有每日调用次数限制
 *    具体请参考各自官网文档
 * 
 * Q4: 可以同时使用两个数据源吗？
 * A: 可以！股票组件使用 iTick，加密货币组件使用沧海数据，互不影响
 */


// ==================== 性能优化建议 ====================

/**
 * 1. 缓存策略
 *    - 沧海数据已实现 5 秒缓存，避免频繁请求
 *    - 可以根据需要调整 cacheTimeout
 * 
 * 2. WebSocket 重连
 *    - iTick 支持断线自动重连（3 秒后）
 *    - 避免频繁重连，设置了重连定时器
 * 
 * 3. 数据点限制
 *    - 图表最多显示 30 个数据点，避免内存泄漏
 *    - 可以通过 MAX_DATA_POINTS 调整
 * 
 * 4. 按需订阅
 *    - 只订阅需要的标的，减少带宽消耗
 *    - 切换市场时动态取消/添加订阅
 */


// ==================== 参考资料 ====================

/**
 * 官方文档：
 * - iTick: https://www.itick.org/docs
 * - 沧海数据：https://www.tsanghi.com/docs
 * 
 * API 调试工具：
 * - WebSocket 测试：https://www.websocket.org/echo.html
 * - REST API 测试：Postman
 * 
 * 数据格式参考：
 * - 查看 financial-data-service.js 中的 formatTickData 和 formatKlineData 方法
 */
