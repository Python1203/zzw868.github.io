# 金融AI实时预测完整项目脚手架

这是一个包含后端Python WebSocket服务器和前端React应用的完整示例，支持实时推送股票价格预测和涨跌概率，并动态展示图表。

---

## 目录结构

```
financial-ai-dashboard/
├── backend/
│   ├── server.py
│   └── requirements.txt
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── public/
    └── src/
        ├── App.tsx
        ├── index.tsx
        ├── RealTimeStockChartWithPie.tsx
        └── hooks/
            └── useWebSocketWithReconnect.ts
```

---

## 后端 (Python WebSocket服务器)

### backend/requirements.txt

```
websockets
```

### backend/server.py

```python
import asyncio
import json
import random
import websockets
from datetime import datetime

clients = set()

async def notify_clients():
    while True:
        if clients:
            prediction = {
                "predictedPrice": round(130 + random.uniform(-5, 5), 2),
                "predictedTrendProbability": round(random.uniform(0.4, 0.9), 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            message = json.dumps({"type": "prediction", "data": prediction})
            await asyncio.wait([client.send(message) for client in clients])
        await asyncio.sleep(5)  # 每5秒推送一次

async def handler(websocket, path):
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)

async def main():
    async with websockets.serve(handler, "localhost", 8080):
        await notify_clients()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 前端 (React + TypeScript + Recharts)

### frontend/package.json

```json
{
  "name": "financial-ai-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "recharts": "^2.5.0",
    "typescript": "^4.9.5"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

### frontend/tsconfig.json

```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```

### frontend/src/hooks/useWebSocketWithReconnect.ts

```tsx
import { useEffect, useRef } from "react";

export const useWebSocketWithReconnect = (
  url: string,
  onMessage: (data: any) => void
) => {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const connect = () => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log("WebSocket connected");
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      onMessage(message);
    };

    ws.current.onclose = () => {
      console.log("WebSocket disconnected, retrying in 3s...");
      reconnectTimeout.current = setTimeout(() => {
        connect();
      }, 3000);
    };

    ws.current.onerror = (err) => {
      console.error("WebSocket error:", err);
      ws.current?.close();
    };
  };

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      ws.current?.close();
    };
  }, [url]);

  return ws.current;
};
```

### frontend/src/RealTimeStockChartWithPie.tsx

```tsx
import React, { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { useWebSocketWithReconnect } from "./hooks/useWebSocketWithReconnect";

type Prediction = {
  predictedPrice: number;
  predictedTrendProbability: number;
  timestamp: string;
};

const COLORS = ["#82ca9d", "#ff4d4f"]; // 绿色涨，红色跌

const RealTimeStockChartWithPie = () => {
  const [data, setData] = useState<{ time: string; price: number }[]>([]);
  const [latestPrediction, setLatestPrediction] = useState<Prediction | null>(
    null
  );

  useWebSocketWithReconnect("ws://localhost:8080", (message) => {
    if (message.type === "prediction") {
      const pred: Prediction = message.data;
      setLatestPrediction(pred);

      setData((prevData) => {
        const newEntry = {
          time: new Date(pred.timestamp).toLocaleTimeString(),
          price: Number(pred.predictedPrice),
        };
        const updatedData = [...prevData, newEntry].slice(-30);
        return updatedData;
      });
    }
  });

  // 饼图数据，涨和跌概率
  const pieData =
    latestPrediction
      ? [
          { name: "涨", value: latestPrediction.predictedTrendProbability },
          { name: "跌", value: 1 - latestPrediction.predictedTrendProbability },
        ]
      : [];

  return (
    <div className="p-4 max-w-4xl mx-auto border rounded shadow grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h2 className="text-xl font-bold mb-4">实时股票价格预测趋势</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={data}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" minTickGap={20} />
            <YAxis domain={["auto", "auto"]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#8884d8"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
        {latestPrediction && (
          <div className="mt-4 text-center">
            <p className="text-lg">
              最新预测价格：<strong>{latestPrediction.predictedPrice.toFixed(2)}</strong> 元
            </p>
            <p className="text-sm text-gray-500 mt-1">
              更新时间：{new Date(latestPrediction.timestamp).toLocaleTimeString()}
            </p>
          </div>
        )}
      </div>

      <div>
        <h2 className="text-xl font-bold mb-4">涨跌概率</h2>
        {latestPrediction ? (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) =>
                  `${name}: ${(percent! * 100).toFixed(1)}%`
                }
              >
                {pieData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index]} />
                ))}
              </Pie>
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-center">等待数据...</p>
        )}
      </div>
    </div>
  );
};

export default RealTimeStockChartWithPie;
```

### frontend/src/App.tsx

```tsx
import React from "react";
import RealTimeStockChartWithPie from "./RealTimeStockChartWithPie";

const App = () => {
  return (
    <div>
      <RealTimeStockChartWithPie />
    </div>
  );
};

export default App;
```

### frontend/src/index.tsx

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root")!);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

## 运行说明

1. **启动后端**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows 用 `venv\Scripts\activate`
pip install -r requirements.txt
python server.py
```

2. **启动前端**

```bash
cd frontend
npm install
npm start
```

3. 打开浏览器访问 `http://localhost:3000`，即可看到实时更新的股票价格预测与涨跌概率图表。

---

如果你需要，我可以帮你：

- 添加用户认证和权限管理  
- 集成真实AI模型预测逻辑  
- 部署到云服务器和生产环境配置  

随时告诉我！