# 金融AI实时预测系统

这是一个完整的金融AI实时预测项目，包含后端 Python WebSocket 服务器和前端 React 应用，支持实时推送股票价格预测和涨跌概率，并动态展示图表。

## 📁 项目结构

```
financial-ai-dashboard/
├── backend/              # 后端服务
│   ├── server.py        # WebSocket 服务器
│   └── requirements.txt # Python 依赖
├── frontend/            # 前端应用
│   ├── public/         # 静态资源
│   ├── src/            # 源代码
│   │   ├── hooks/      # 自定义 Hooks
│   │   │   └── useWebSocketWithReconnect.ts
│   │   ├── App.tsx     # 主应用组件
│   │   ├── index.tsx   # 入口文件
│   │   └── RealTimeStockChartWithPie.tsx  # 股票图表组件
│   ├── package.json    # 项目依赖
│   └── tsconfig.json   # TypeScript 配置
└── README.md          # 项目文档
```

## 🚀 快速开始

### 1. 启动后端服务

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python server.py
```

启动成功后会显示：
```
🚀 金融AI实时预测服务器启动中...
✅ 服务器已启动，监听端口：ws://localhost:8080
```

### 2. 启动前端应用

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

浏览器会自动打开 `http://localhost:3000`

## ✨ 功能特性

### 后端特性
- ✅ WebSocket 实时通信
- ✅ 多客户端支持
- ✅ 每 5 秒自动推送数据
- ✅ 连接状态管理
- ✅ 模拟 AI 预测算法

### 前端特性
- ✅ React 18 + TypeScript
- ✅ Recharts 数据可视化
- ✅ WebSocket 自动重连（指数退避）
- ✅ 实时价格趋势折线图
- ✅ 涨跌概率饼图
- ✅ 响应式设计
- ✅ Tailwind CSS 样式
- ✅ 连接状态指示器

## 📊 数据格式

### WebSocket 推送数据

```json
{
  "type": "prediction",
  "data": {
    "predictedPrice": 128.45,
    "predictedTrendProbability": 0.75,
    "timestamp": "2026-03-15T10:30:00.000Z"
  }
}
```

- `predictedPrice`: 预测的股票价格
- `predictedTrendProbability`: 上涨概率 (0-1)
- `timestamp`: 数据生成时间戳

## 🎨 界面预览

系统提供两个主要视图：

1. **价格趋势图**（左侧）
   - 实时更新的折线图
   - 显示最新 30 条数据
   - 当前价格突出显示

2. **涨跌概率图**（右侧）
   - 饼图展示涨跌概率分布
   - 绿色代表上涨
   - 红色代表下跌
   - 详细百分比统计

## 🔧 技术栈

### 后端
- Python 3.8+
- websockets (WebSocket 库)
- asyncio (异步 IO)

### 前端
- React 18
- TypeScript 4.9+
- Recharts 2.5+
- react-scripts 5.0+

## ⚙️ 配置说明

### 修改 WebSocket 地址

在 `frontend/src/RealTimeStockChartWithPie.tsx` 中：

```typescript
useWebSocketWithReconnect("ws://your-server:8080", (message) => {
  // ...
});
```

### 调整推送频率

在 `backend/server.py` 中修改：

```python
await asyncio.sleep(5)  # 改为其他秒数
```

### 修改数据范围

在 `backend/server.py` 中修改：

```python
"predictedPrice": round(130 + random.uniform(-5, 5), 2)
# 修改 130 为基础价格，-5 到 5 为波动范围
```

## 🛠️ 开发工具

### 后端调试

```bash
# 查看 Python 版本
python --version

# 验证依赖安装
pip list | grep websockets
```

### 前端调试

```bash
# 查看 Node 版本
node --version

# 查看 npm 版本
npm --version

# 清理缓存
npm cache clean --force
```

## 📝 常见问题

### Q: WebSocket 连接失败？
A: 确保后端服务器已启动，并且端口 8080 未被占用。

### Q: 前端无法访问后端？
A: 检查 CORS 设置，确保前后端在同一域或使用代理。

### Q: 图表不显示？
A: 检查浏览器控制台是否有错误，确保已安装所有依赖。

### Q: 数据更新太慢？
A: 可以减少后端的 `asyncio.sleep()` 时间间隔。

## 🚀 部署建议

### 生产环境部署

1. **后端部署**
   ```bash
   # 使用 gunicorn 运行
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8080 server:app
   ```

2. **前端部署**
   ```bash
   # 构建生产版本
   npm run build
   
   # 部署到 Nginx 或其他 Web 服务器
   ```

3. **环境变量配置**
   - 设置 WebSocket 服务器地址
   - 配置 API 密钥（如使用真实数据源）

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**注意**: 本系统仅为演示目的，不构成投资建议。实际投资请咨询专业人士。
