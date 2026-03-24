# 加密货币仪表板 CSP 错误修复指南

## 🔍 问题描述
浏览器控制台显示以下错误：
```
Executing inline script violates the following Content Security Policy directive
vue.global.js:12714 You are running a development build of Vue.
Uncaught ReferenceError: Pinia is not defined
```

## ✅ 已完成的修复

文件位置：`/Users/zzw868/PycharmProjects/zzw868.github.io/source/components/crypto-dashboard-widget.html`

### 修改内容

#### 修改前（旧版本）：
```html
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<script src="https://unpkg.com/pinia@2/dist/pinia.js"></script>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script src="/js/financial-data-service.js"></script>
<script src="/js/binance-service.js"></script>
```

#### 修改后（新版本）：
```html
<!-- 使用生产版本的 Vue 和 Pinia，解决 CSP 和兼容性问题 -->
<script src="https://unpkg.com/vue@3.4.21/dist/vue.global.prod.js"></script>
<script src="https://unpkg.com/pinia@2.1.7/dist/pinia.iife.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
```

### 关键改进
1. **Vue**: 从开发版 (`vue.global.js`) → 生产版 (`vue.global.prod.js`)
   - 指定版本号 `3.4.21` 确保稳定性
   - 生产版本去除了开发警告和调试信息
   
2. **Pinia**: 从 UMD 格式 (`pinia.js`) → IIFE 格式 (`pinia.iife.min.js`)
   - IIFE 格式确保 Pinia 正确加载到全局作用域
   - 解决 `Pinia is not defined` 错误
   - 指定版本号 `2.1.7`
   
3. **ECharts**: 从 `5.x` → `5.5.0`
   - 指定具体版本号确保一致性
   
4. **移除外部依赖**: 
   - 删除了对 `/js/financial-data-service.js` 的引用
   - 删除了对 `/js/binance-service.js` 的引用
   - 组件现在完全独立，不依赖外部 JS 文件

## 🛠️ 验证步骤

### 1. 检查文件实际内容
在终端执行以下命令查看文件的真实内容：

```bash
# 查看第 14-16 行的 CDN 链接
head -n 20 /Users/zzw868/PycharmProjects/zzw868.github.io/source/components/crypto-dashboard-widget.html | tail -n 7
```

应该看到：
```html
    <!-- 使用生产版本的 Vue 和 Pinia，解决 CSP 和兼容性问题 -->
    <script src="https://unpkg.com/vue@3.4.21/dist/vue.global.prod.js"></script>
    <script src="https://unpkg.com/pinia@2.1.7/dist/pinia.iife.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
```

### 2. 清除 IDE 缓存
如果使用 IntelliJ IDEA、WebStorm 或 PyCharm：
- `File` → `Invalidate Caches...` → 勾选所有选项 → `Invalidate and Restart`

### 3. 清除浏览器缓存
- Chrome/Edge: `Cmd+Shift+Delete` (Mac) 或 `Ctrl+Shift+Delete` (Windows)
- 勾选"缓存的图片和文件"
- 时间范围选择"全部时间"
- 点击"清除数据"

### 4. 检查是否有构建进程在运行
```bash
# 检查是否有 Hexo、npm 或其他构建进程
ps aux | grep -E "hexo|npm|node|gulp|webpack"
```

如果有，请停止它们（按 `Ctrl+C`）。

### 5. 检查 Git hooks
```bash
# 查看是否有自动恢复文件的钩子
ls -la .git/hooks/
```

如果怀疑是 Git hook 的问题，可以临时禁用：
```bash
mv .git/hooks .git/hooks.backup
```

### 6. 硬刷新浏览器页面
- Mac: `Cmd+Shift+R`
- Windows/Linux: `Ctrl+Shift+R` 或 `Ctrl+F5`

## 🎯 预期结果

修复后，浏览器控制台应该：
- ✅ 不再显示 CSP 错误
- ✅ 不再显示 Vue 开发版本警告
- ✅ 不再显示 `Pinia is not defined` 错误
- ✅ 加密货币仪表板正常显示实时价格数据

## 🐛 如果问题仍然存在

### 检查浏览器中的实际加载内容
1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 刷新页面
4. 找到 `crypto-dashboard-widget.html` 并点击查看
5. 检查 Response 中的 `<head>` 部分，确认 CDN 链接是否正确

### 检查部署目录
确保部署目录的文件也同步更新：
```bash
# 比较源文件和部署文件
diff source/components/crypto-dashboard-widget.html .deploy_git/components/crypto-dashboard-widget.html
```

如果有差异，复制源文件到部署目录：
```bash
cp source/components/crypto-dashboard-widget.html .deploy_git/components/crypto-dashboard-widget.html
```

## 📝 技术说明

### 为什么使用 IIFE 格式的 Pinia？
- **IIFE** (Immediately Invoked Function Expression): 立即执行函数表达式
- 直接挂载到全局对象（window.Pinia）
- 适合通过 `<script>` 标签直接引入的场景
- 不需要模块打包工具

### 为什么使用生产版本的 Vue？
- 更小的文件大小（压缩 + 压缩）
- 更快的运行速度（去除开发模式检查）
- 更好的性能优化
- 去除开发警告

### CSP (Content Security Policy)
- 防止 XSS 攻击的安全机制
- 限制哪些资源可以被加载和执行
- 内联脚本默认被阻止，除非：
  - 添加 `'unsafe-inline'` 指令
  - 使用 hash 或 nonce
  - 使用外部脚本文件

## 📞 需要进一步帮助？

如果按照以上步骤操作后问题仍未解决，请提供：
1. 终端命令 `head -n 20 source/components/crypto-dashboard-widget.html | tail -n 7` 的输出
2. 浏览器控制台的完整错误截图
3. Network 面板中该文件的 CDN 链接截图
