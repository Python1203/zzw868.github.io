# useBinanceWS Hook - 快速参考

## 🚀 30 秒快速开始

```jsx
// 1️⃣ 导入 Hook
import { useBinanceWS } from './js/useBinanceWS';

// 2️⃣ 在组件中使用
function App() {
  const data = useBinanceWS(['btcusdt', 'ethusdt']);
  
  return (
    <div>
      {data.BTCUSDT && (
        <p>BTC: ${data.BTCUSDT.price} ({data.BTCUSDT.change}%)</p>
      )}
    </div>
  );
}
```

---

## 📦 三个 Hook 任你选

### 1. useBinanceWS(symbols)
**用途**: 监控多个币种
```javascript
const data = useBinanceWS(['btcusdt', 'ethusdt', 'bnbusdt']);
// 返回：{ BTCUSDT: {...}, ETHUSDT: {...}, BNBUSDT: {...} }
```

### 2. useSingleCrypto(symbol)
**用途**: 监控单个币种
```javascript
const btc = useSingleCrypto('btcusdt');
// 返回：{ price: '45000', change: '2.5', ... } 或 null
```

### 3. useCryptoPortfolio(symbols)
**用途**: 投资组合视图（已排序）
```javascript
const portfolio = useCryptoPortfolio(['btcusdt', 'ethusdt']);
// 返回：[{ symbol: 'BTCUSDT', price: '45000', change: '2.5', ... }, ...]
```

---

## 🎯 常用场景代码片段

### 场景 1: 价格卡片
```jsx
function CryptoCard({ symbol }) {
  const data = useSingleCrypto(symbol);
  
  if (!data) return <div>加载中...</div>;
  
  return (
    <div className="card">
      <h3>{symbol}</h3>
      <p className="price">${data.price}</p>
      <p className={`change ${parseFloat(data.change) >= 0 ? 'up' : 'down'}`}>
        {data.change}%
      </p>
    </div>
  );
}
```

### 场景 2: 价格预警
```jsx
function PriceAlert({ targetPrice }) {
  const btc = useSingleCrypto('btcusdt');
  
  useEffect(() => {
    if (btc && parseFloat(btc.price) > targetPrice) {
      console.log('🚨 BTC 突破预警价!');
    }
  }, [btc, targetPrice]);
  
  return null;
}
```

### 场景 3: 多币种列表
```jsx
function CryptoList() {
  const data = useBinanceWS(['btcusdt', 'ethusdt', 'solusdt']);
  
  return (
    <ul>
      {Object.entries(data).map(([symbol, info]) => (
        <li key={symbol}>
          {symbol}: ${info.price} ({info.change}%)
        </li>
      ))}
    </ul>
  );
}
```

---

## 📊 数据字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `price` | string | 当前价格 | "45230.50" |
| `change` | string | 24h 涨跌幅 (%) | "2.35" |
| `high` | string | 24h 最高价 | "46000.00" |
| `low` | string | 24h 最低价 | "44500.00" |
| `volume` | string | 24h 成交量 | "12345.67" |
| `timestamp` | number | 时间戳 | 1234567890 |

---

## ⚡ 性能提示

### ✅ 推荐做法
```javascript
// 好的做法 - 稳定的 symbols 数组
const symbols = useMemo(() => ['btcusdt', 'ethusdt'], []);
const data = useBinanceWS(symbols);

// 好的做法 - 直接传字面量
const data = useBinanceWS(['btcusdt', 'ethusdt']);
```

### ❌ 避免的做法
```javascript
// 不好 - 每次渲染都创建新数组
const data = useBinanceWS(['btcusdt', 'ethusdt']); // 在循环中

// 不好 - 不稳定的引用
const symbols = ['btcusdt']; // 在组件内部定义
const data = useBinanceWS(symbols);
```

---

## 🔧 自定义配置

### 修改重连策略
编辑 `useBinanceWS.js`:
```javascript
const maxReconnectAttempts = 10; // 最大重连次数
const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000); // 最大 30 秒
```

### 添加数据过滤
```javascript
ws.current.onmessage = (event) => {
  const message = JSON.parse(event.data);
  const { stream, data: rawData } = message;
  
  // 只处理特定条件的数据
  if (parseFloat(rawData.c) > 1000) {
    setData(prev => ({ ...prev, ... }));
  }
};
```

---

## 🛠️ 常见问题速查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 连接失败 | 网络问题 | 检查网络，确认能访问 Binance |
| 数据不更新 | 组件卸载 | 确保组件保持挂载状态 |
| 内存泄漏 | 未清理 | Hook 已自动处理，无需担心 |
| 页面卡顿 | 币种太多 | 减少监控的币种数量 (<20) |

---

## 💻 完整示例

```jsx
import React, { useState } from 'react';
import { useBinanceWS } from './js/useBinanceWS';

function CryptoDashboard() {
  const [selectedSymbols] = useState(['btcusdt', 'ethusdt', 'bnbusdt']);
  const data = useBinanceWS(selectedSymbols);

  return (
    <div className="dashboard">
      <h1>加密货币实时看板</h1>
      
      <div className="grid">
        {Object.entries(data).map(([symbol, info]) => (
          <div key={symbol} className="card">
            <h2>{symbol.replace('USDT', '')}</h2>
            <p className="price">${info.price}</p>
            <p 
              className="change"
              style={{
                color: parseFloat(info.change) >= 0 ? 'green' : 'red'
              }}
            >
              {parseFloat(info.change) >= 0 ? '+' : ''}{info.change}%
            </p>
            
            <div className="stats">
              <div>24h 高：${info.high}</div>
              <div>24h 低：${info.low}</div>
              <div>成交量：{info.volume}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CryptoDashboard;
```

---

## 📱 演示页面

查看完整演示：
```bash
# 启动本地服务器
hexo server

# 访问演示页面
open http://localhost:4000/components/crypto-price-widget.html
```

---

## 🔗 更多资源

- 📖 完整文档：`source/js/README_BINANCE_HOOK.md`
- 💻 示例代码：`source/components/crypto-price-widget.html`
- 📝 总结报告：`BINANCE_HOOK_SUMMARY.md`

---

**最后更新**: 2026-03-24  
**版本**: v1.0.0  
**License**: MIT
