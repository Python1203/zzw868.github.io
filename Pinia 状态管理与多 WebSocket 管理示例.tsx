import {defineStore} from 'pinia';
import {reactive, ref} from 'vue';

// 工具函数：防抖
function debounce(fn, delay) {
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

export const useMarketStore = defineStore('market', () => {
  // 选中市场、时间范围、指标
  const selectedMarket = ref('BTC-USD');
  const selectedRange = ref('1m');
  const selectedIndicator = ref('none');

  // 多个交易所 WebSocket 实例管理
  const sockets = reactive({});

  // 数据状态，示例结构
  const klineData = ref([]); // [timestamp, open, close, low, high, volume][]
  const depthData = reactive({
    bids: [],
    asks: [],
  });
  const priceData = ref([]); // [timeStr, price][]
  const volumeData = ref([]); // [timeStr, volume][]

  // 连接 WebSocket，支持多个交易所和频道
  function connectWebSocket(exchange, market, range) {
    // 关闭已有连接（如果有）
    if (sockets[exchange]) {
      try {
        sockets[exchange].close();
      } catch {}
      delete sockets[exchange];
    }

    // 根据交易所构造不同 WebSocket URL 和订阅逻辑
    let url = '';
    let subscribeMsg = null;

    if (exchange === 'binance') {
      // Binance示例
      const streamName = `${market.toLowerCase().replace('-', '')}@kline_${range}`;
      url = `wss://stream.binance.com:9443/ws/${streamName}`;
    } else if (exchange === 'huobi') {
      // Huobi示例（需根据官方文档调整）
      url = 'wss://api.huobi.pro/ws';
      subscribeMsg = JSON.stringify({
        sub: `market.${market.toLowerCase()}.kline.${range}`,
        id: `id_${market}_${range}`,
      });
    } else {
      console.warn('未知交易所:', exchange);
      return;
    }

    const ws = new WebSocket(url);
    sockets[exchange] = ws;

    ws.onopen = () => {
      console.log(`[${exchange}] WebSocket已连接`, url);
      if (subscribeMsg) ws.send(subscribeMsg);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        // 解析消息，更新对应数据
        if (exchange === 'binance') {
          if (msg.e === 'kline') {
            const k = msg.k;
            updateKline([k.t, parseFloat(k.o), parseFloat(k.c), parseFloat(k.l), parseFloat(k.h), parseFloat(k.v)]);
          }
        } else if (exchange === 'huobi') {
          if (msg.tick && msg.tick.kline) {
            const k = msg.tick.kline;
            // Huobi kline数据格式示例，需根据实际文档调整
            updateKline([k.id * 1000, k.open, k.close, k.low, k.high, k.vol]);
          }
        }
      } catch (e) {
        console.error(`[${exchange}] WebSocket消息解析错误`, e);
      }
    };

    ws.onclose = () => {
      console.log(`[${exchange}] WebSocket连接关闭`);
      delete sockets[exchange];
    };

    ws.onerror = (err) => {
      console.error(`[${exchange}] WebSocket错误`, err);
    };
  }

  // 更新K线数据，保持最新30条，防抖批量更新
  const updateKline = debounce((newCandle) => {
    const idx = klineData.value.findIndex(c => c[0] === newCandle[0]);
    if (idx !== -1) {
      klineData.value[idx] = newCandle;
    } else {
      klineData.value.push(newCandle);
      if (klineData.value.length > 30) {
        klineData.value.shift();
      }
    }
  }, 200);

  // 关闭所有WebSocket连接，清理资源
  function closeAllSockets() {
    Object.keys(sockets).forEach(exchange => {
      try {
        sockets[exchange].close();
      } catch {}
      delete sockets[exchange];
    });
  }

  // 切换市场时，关闭旧连接，开启新连接
  function switchMarket(market, range) {
    closeAllSockets();
    // 这里示例连接两个交易所数据
    connectWebSocket('binance', market, range);
    connectWebSocket('huobi', market, range);
  }

  return {
    selectedMarket,
    selectedRange,
    selectedIndicator,
    klineData,
    depthData,
    priceData,
    volumeData,
    connectWebSocket,
    switchMarket,
    closeAllSockets,
    updateKline,
  };
});