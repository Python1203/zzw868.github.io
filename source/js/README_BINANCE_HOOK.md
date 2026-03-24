# useBinanceWS Hook - Binance 实时价格数据

## 📚 概述

`useBinanceWS` 是一个 React 自定义 Hook，用于连接 Binance WebSocket 获取加密货币实时价格数据。支持自动重连、多币种监控和数据清理。

## ✨ 特性

- 🔌 **WebSocket 连接** - 直连 Binance 官方 WebSocket
- 🔄 **自动重连** - 指数退避策略，最多重试 5 次
- 📊 **多币种支持** - 同时监控多个交易对
- 🧹 **自动清理** - 组件卸载时自动断开连接
- 🎯 **类型安全** - 完整的数据结构定义
- ♻️ **可复用** - 可在多个组件中使用

## 📦 数据结构

返回的数据格式：
```javascript
{
  BTCUSDT: {
    price: '45230.50',      // 当前价格
    change: '2.35',         // 24h 涨跌幅 (%)
    high: '46000.00',       // 24h 最高价
    low: '44500.00',        // 24h 最低价
    volume: '12345.67',     // 24h 成交量
    timestamp: 1234567890   // 时间戳
  },
  ETHUSDT: { ... }
}
```

## 🚀 快速开始

### 1. 基础用法

```jsx
import React from 'react';
import { useBinanceWS } from './useBinanceWS';

const CryptoTracker = () => {
  const data = useBinanceWS(['btcusdt', 'ethusdt']);

  return (
    <div>
      {Object.entries(data).map(([symbol, info]) => (
        <div key={symbol}>
          <h3>{symbol}</h3>
          <p>价格：${info.price}</p>
          <p>24h 涨跌：{info.change}%</p>
        </div>
      ))}
    </div>
  );
};
```

### 2. 单个币种 Hook

```jsx
import { useSingleCrypto } from './useBinanceWS';

const BTCCard = () => {
  const btcData = useSingleCrypto('btcusdt');

  if (!btcData) return <div>加载中...</div>;

  return (
    <div>
      <h2>Bitcoin</h2>
      <p>${btcData.price}</p>
      <p style={{ color: parseFloat(btcData.change) >= 0 ? 'green' : 'red' }}>
        {btcData.change}%
      </p>
    </div>
  );
};
```

### 3. 投资组合视图

```jsx
import { useCryptoPortfolio } from './useBinanceWS';

const Portfolio = () => {
  const portfolio = useCryptoPortfolio(['btcusdt', 'ethusdt', 'bnbusdt']);

  return (
    <div>
      {portfolio.map(coin => (
        <div key={coin.symbol}>
          <span>{coin.symbol}</span>
          <span style={{ color: coin.priceChangeColor }}>
            ${coin.price} ({coin.change}%)
          </span>
        </div>
      ))}
    </div>
  );
};
```

## 🎯 完整示例组件

查看 `source/components/crypto-price-widget.html` 获取完整的演示组件。

## ⚙️ API 参数

### useBinanceWS(symbols)

**参数:**
- `symbols` (string[]): 交易对列表，例如 `['btcusdt', 'ethusdt']`

**返回:**
- `Object`: 包含所有币种实时数据的对象

### useSingleCrypto(symbol)

**参数:**
- `symbol` (string): 单个交易对，例如 `'btcusdt'`

**返回:**
- `Object | null`: 该币种的数据或 null

### useCryptoPortfolio(symbols)

**参数:**
- `symbols` (string[]): 币种列表

**返回:**
- `Array`: 排序后的币种数据数组（按交易量降序）

## 🔧 高级配置

### 自定义重连策略

修改 Hook 内部的重连参数：

```javascript
const maxReconnectAttempts = 10; // 最大重连次数
const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000); // 最大 30 秒
```

### 添加数据过滤

```javascript
ws.current.onmessage = (event) => {
  const message = JSON.parse(event.data);
  const { stream, data: rawData } = message;
  
  // 只处理价格大于某个值的数据
  if (parseFloat(rawData.c) > 1000) {
    setData(prev => ({ ...prev, ... }));
  }
};
```

## 🛠️ 故障排除

### 问题：WebSocket 连接失败

**解决方案:**
1. 检查网络连接
2. 确认 Binance API 可访问性
3. 查看控制台错误信息
4. 尝试使用代理服务器

### 问题：数据不更新

**解决方案:**
1. 检查组件是否保持挂载
2. 确认 symbols 参数未频繁变化
3. 查看 WebSocket 连接状态

### 问题：内存泄漏

**解决方案:**
确保组件卸载时清理：

```javascript
useEffect(() => {
  return () => {
    // Hook 会自动清理
  };
}, []);
```

## 📝 注意事项

1. **API 限制**: Binance WebSocket 有连接数限制，不要创建过多连接
2. **性能优化**: 监控的币种不宜过多（建议 < 20 个）
3. **错误处理**: 生产环境应添加错误边界
4. **HTTPS**: 在 HTTPS 环境下运行，避免混合内容警告

## 🔗 相关资源

- [Binance WebSocket API 文档](https://binance-docs.github.io/apidocs/spot/en/#websocket-market-streams)
- [React Hooks 最佳实践](https://react.dev/reference/react)
- [WebSocket MDN 文档](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## 💡 使用场景

- ✅ 加密货币价格追踪看板
- ✅ 实时交易信号提醒
- ✅ 投资组合管理工具
- ✅ 价格预警系统
- ✅ 数据分析仪表板

## 📄 许可证

MIT License

---

**作者**: zzw868  
**创建时间**: 2026-03-24  
**最后更新**: 2026-03-24
