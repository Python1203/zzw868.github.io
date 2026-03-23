# 🔗 金融AI实时预测 - 网页嵌入指南

## 📋 目录

1. [快速开始](#快速开始)
2. [嵌入方式](#嵌入方式)
3. [样式自定义](#样式自定义)
4. [响应式适配](#响应式适配)
5. [示例代码](#示例代码)

---

## 🚀 快速开始

### 方式一：iframe 嵌入（推荐）

最简单的方式是使用 `<iframe>` 标签，将金融AI实时预测系统嵌入到你的网页中。

#### 基础代码

```html
<iframe 
    src="http://localhost:3000" 
    width="100%" 
    height="800" 
    frameborder="0" 
    allowfullscreen>
</iframe>
```

#### 优点
- ✅ 简单易用，复制粘贴即可
- ✅ 完全独立，不影响父页面
- ✅ 自动包含所有功能
- ✅ WebSocket 实时数据正常推送

---

### 方式二：组件嵌入（高级）

如果你使用的是 Vue/React 等现代框架，可以直接集成组件。

#### Vue 项目

```vue
<template>
  <div class="financial-ai-widget">
    <!-- 在这里集成 React 组件或使用微前端方案 -->
  </div>
</template>

<script>
// 使用微前端或 Web Components 方案集成
</script>
```

#### React 项目

```jsx
import FinancialAIWidget from 'financial-ai-widget';

function App() {
  return (
    <div className="widget-container">
      <FinancialAIWidget />
    </div>
  );
}
```

---

## 🎨 样式自定义

### iframe 样式调整

```html
<!-- 自适应宽度 -->
<iframe 
    src="http://localhost:3000" 
    style="width: 100%; height: 800px; border: none; overflow: hidden;"
    allowfullscreen>
</iframe>

<!-- 固定宽度居中 -->
<iframe 
    src="http://localhost:3000" 
    style="width: 1200px; height: 800px; border: none; display: block; margin: 0 auto;"
    allowfullscreen>
</iframe>

<!-- 带圆角和阴影 -->
<iframe 
    src="http://localhost:3000" 
    style="width: 100%; height: 800px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);"
    allowfullscreen>
</iframe>
```

### 容器样式

```css
.widget-container {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    background: #f7fafc;
    border-radius: 15px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}
```

---

## 📱 响应式适配

### 使用 CSS 媒体查询

```css
/* 移动端优化 */
@media (max-width: 768px) {
    .widget-container iframe {
        height: 600px !important;
    }
}

/* 平板优化 */
@media (min-width: 769px) and (max-width: 1024px) {
    .widget-container iframe {
        height: 700px !important;
    }
}

/* 桌面端 */
@media (min-width: 1025px) {
    .widget-container iframe {
        height: 800px;
    }
}
```

### 使用 JavaScript 动态调整

```javascript
function adjustIframeHeight() {
    const iframe = document.querySelector('.financial-widget');
    if (window.innerWidth < 768) {
        iframe.style.height = '600px';
    } else if (window.innerWidth < 1024) {
        iframe.style.height = '700px';
    } else {
        iframe.style.height = '800px';
    }
}

window.addEventListener('resize', adjustIframeHeight);
adjustIframeHeight(); // 初始化
```

---

## 💡 示例代码

### 完整 HTML 示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的网站 - 金融AI预测</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }

        h1 {
            text-align: center;
            color: #2d3748;
            margin-bottom: 30px;
        }

        .widget-wrapper {
            position: relative;
            overflow: hidden;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        iframe {
            display: block;
            width: 100%;
        }

        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            iframe {
                height: 600px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 金融AI实时预测系统</h1>
        
        <div class="widget-wrapper">
            <iframe 
                src="http://localhost:3000" 
                style="height: 800px;"
                frameborder="0"
                allowfullscreen>
            </iframe>
        </div>
    </div>

    <script>
        // 动态调整高度
        function adjustHeight() {
            const iframe = document.querySelector('iframe');
            if (window.innerWidth < 768) {
                iframe.style.height = '600px';
            } else {
                iframe.style.height = '800px';
            }
        }

        window.addEventListener('resize', adjustHeight);
        adjustHeight();
    </script>
</body>
</html>
```

---

## 🔧 在 Hexo 博客中嵌入

### 修改文章 Markdown

在你的 Hexo 文章 Markdown 文件中添加:

```markdown
---
title: 财经期刊FM-Radio
date: 2021-05-20
tags: [金融，AI, 预测]
---

# 金融AI实时预测系统

<iframe 
    src="/financial-ai-dashboard/index.html" 
    width="100%" 
    height="800" 
    frameborder="0"
    style="border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
</iframe>

## 功能介绍

- 📈 实时价格趋势预测
- 📊 涨跌概率分析
- ⚡ 每 5 秒自动更新
- 🎨 现代化 UI 设计

---

**提示**: 确保已将 `financial-ai-dashboard` 目录部署到服务器上。
```

### 配置 Hexo

在 `_config.yml` 中添加:

```yaml
# 允许 iframe
external_link:
  enable: true
  field: site
  exclude: ''
```

---

## 🌐 部署到生产环境

### 1. 构建前端

```bash
cd frontend
npm run build
```

### 2. 配置服务器

#### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /financial-ai/ {
        alias /path/to/financial-ai-dashboard/frontend/build/;
        try_files $uri $uri/ /index.html;
    }

    # WebSocket 支持
    location /ws {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 3. 修改 iframe 地址

```html
<!-- 开发环境 -->
<iframe src="http://localhost:3000"></iframe>

<!-- 生产环境 -->
<iframe src="https://your-domain.com/financial-ai/"></iframe>
```

---

## ⚙️ 高级配置

### 跨域访问设置

如果你的 iframe 需要跨域访问，需要在后端配置 CORS:

#### Python WebSocket 服务器

```python
import websockets
from websockets.server import serve

async def handler(websocket, path):
    # 处理连接
    pass

async def main():
    async with serve(
        handler, 
        "0.0.0.0",  # 监听所有接口
        8080,
        origins=["*"]  # 允许所有来源，生产环境应指定具体域名
    ):
        await asyncio.Future()

asyncio.run(main())
```

### 性能优化

```html
<!-- 懒加载 iframe -->
<iframe 
    src="http://localhost:3000" 
    loading="lazy"
    width="100%" 
    height="800" 
    frameborder="0">
</iframe>

<!-- 预连接 -->
<link rel="preconnect" href="http://localhost:3000">
```

---

## 🎯 最佳实践

### 1. 用户体验

- ✅ 添加加载动画
- ✅ 提供错误提示
- ✅ 显示连接状态
- ✅ 优化移动端体验

### 2. 性能

- ✅ 使用 CDN 加速
- ✅ 启用 Gzip 压缩
- ✅ 优化图片资源
- ✅ 合理设置缓存

### 3. 安全

- ✅ 使用 HTTPS
- ✅ 限制 iframe 权限
- ✅ 防止点击劫持
- ✅ 验证用户输入

---

## 🆘 常见问题

### Q1: iframe 不显示内容？

**A:** 检查以下几点:
1. 确认后端和前端服务都已启动
2. 检查端口是否正确
3. 查看浏览器控制台是否有错误
4. 确认没有跨域限制

### Q2: WebSocket 连接失败？

**A:** 
1. 确保 WebSocket 服务器已启动
2. 检查防火墙设置
3. 确认协议是 `ws://` 或 `wss://`
4. 查看网络请求中的 WebSocket 状态

### Q3: 移动端显示不正常？

**A:**
1. 使用响应式设计
2. 调整 iframe 高度
3. 优化触摸交互
4. 测试不同屏幕尺寸

---

## 📞 技术支持

如有问题，请查阅:
- [README.md](README.md) - 完整文档
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [GitHub Issues](https://github.com/your-repo/issues) - 问题反馈

---

**祝你嵌入成功!** 🎉
