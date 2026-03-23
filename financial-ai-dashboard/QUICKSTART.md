# 快速入门指南 🚀

## 5 分钟快速启动

### 方式一：使用自动启动脚本（推荐）

#### macOS / Linux

```bash
# 赋予执行权限
chmod +x start.sh

# 一键启动
./start.sh
```

#### Windows

双击 `start.bat` 文件即可

---

### 方式二：手动启动

#### 1. 启动后端（终端 1）

```bash
cd backend

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动 WebSocket 服务器
python server.py
```

看到以下输出表示成功：
```
🚀 金融AI实时预测服务器启动中...
✅ 服务器已启动，监听端口：ws://localhost:8080
```

#### 2. 启动前端（终端 2）

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

浏览器会自动打开 http://localhost:3000

---

## ✅ 验证安装

### 后端检查

- [ ] Python 版本 >= 3.8
- [ ] websockets 库已安装
- [ ] 服务器运行在 ws://localhost:8080
- [ ] 终端显示"服务器已启动"

### 前端检查

- [ ] Node.js 版本 >= 14
- [ ] 所有 npm 依赖已安装
- [ ] 应用运行在 http://localhost:3000
- [ ] 浏览器能正常访问

### 功能检查

- [ ] 页面显示"金融AI实时预测系统"标题
- [ ] 连接状态显示"🟢 已连接"
- [ ] 价格趋势图开始更新数据
- [ ] 涨跌概率饼图正常显示
- [ ] 数据每 5 秒自动刷新

---

## 🛠️ 常见问题

### Q1: 端口被占用

**错误信息**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8080  # 后端端口
lsof -i :3000  # 前端端口

# 终止进程
kill -9 <PID>
```

### Q2: npm install 失败

**解决方案**:
```bash
# 清理缓存
npm cache clean --force

# 删除 node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### Q3: Python 虚拟环境问题

**解决方案**:
```bash
# 删除旧环境
rm -rf venv

# 重新创建
python3 -m venv venv
```

### Q4: WebSocket 连接失败

**检查清单**:
1. 后端服务器是否启动
2. 端口 8080 是否可访问
3. 防火墙是否阻止连接
4. 浏览器控制台是否有错误

---

## 📱 移动端测试

本系统完全支持移动设备访问：

1. 确保手机和电脑在同一 WiFi 网络
2. 修改前端 WebSocket 地址为电脑 IP
3. 在手机浏览器访问：`http://你的电脑IP:3000`

---

## 🎯 下一步

安装成功后，你可以：

1. 📊 **查看实时数据** - 观察价格和概率变化
2. 🎨 **自定义样式** - 修改 Tailwind CSS 类名
3. 🔧 **调整参数** - 修改后端数据生成逻辑
4. 📈 **集成真实数据** - 接入真实的股票 API
5. 🚀 **部署上线** - 发布到生产环境

---

## 📞 需要帮助？

如果遇到问题：

1. 查看 [README.md](README.md) 详细文档
2. 检查浏览器和终端的错误日志
3. 重启后端和前端服务
4. 清除缓存后重试

祝你使用愉快！🎉
