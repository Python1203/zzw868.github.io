# 🚀 博客修复与优化快速指南

## ⚡ 一键修复（推荐）

```bash
# 运行完整优化修复流程
./optimize-and-fix-blog.sh
```

这个脚本会自动：
- ✅ 检查并修复依赖版本
- ✅ 清理并重装所有依赖
- ✅ 验证 Hexo 配置
- ✅ 生成静态文件
- ✅ 检查关键文件完整性
- ✅ 提供优化建议

---

## 📋 常见问题速查

### 1. npm install 失败
**错误**: `No matching version found for hexo-pwa@^1.1.0`  
**解决**: 
```bash
# 手动修复 package.json
sed -i.bak 's/"hexo-pwa": "\^1.1.0"/"hexo-pwa": "^0.1.3"/g' package.json
npm install
```

### 2. hexo-pwa 报错
**错误**: `Cannot read properties of undefined (reading 'manifest')`  
**影响**: PWA 功能受限，但不影响博客主要内容  
**解决**: 忽略该错误，博客仍可正常工作

### 3. 主题不显示
**解决**:
```bash
# 重新创建主题链接
mkdir -p themes
ln -sf ../node_modules/hexo-theme-next themes/next
hexo clean && hexo generate
```

### 4. 文章不更新
**解决**:
```bash
# 清理缓存
hexo clean
# 重新生成
hexo generate
```

---

## 🔧 日常维护命令

### 本地开发
```bash
# 启动本地服务器
hexo server

# 访问地址
http://localhost:4000
```

### 部署到 GitHub
```bash
# 方法 1: 标准流程
hexo clean && hexo generate && hexo deploy

# 方法 2: 自动修复并推送
./auto-fix-blog.sh

# 方法 3: 紧急部署
./emergency-deploy.sh
```

### 定期维护
```bash
# 每月运行一次优化修复脚本
./optimize-and-fix-blog.sh
```

---

## 📊 检查清单

在部署前，确保：
- [ ] 运行 `hexo clean` 清理缓存
- [ ] 运行 `hexo generate` 成功生成文件
- [ ] 检查 `public/` 目录包含所有必要文件
- [ ] 本地测试正常访问
- [ ] Git 提交所有变更

---

## 🛠️ 工具脚本说明

| 脚本 | 用途 | 使用场景 |
|------|------|----------|
| `optimize-and-fix-blog.sh` | 全面优化修复 | 定期维护、遇到问题时 |
| `auto-fix-blog.sh` | 自动修复并推送 | 日常更新博客 |
| `emergency-deploy.sh` | 紧急手动部署 | GitHub Actions 失败时 |

---

## 📝 配置文件位置

- **Hexo 主配置**: `_config.yml`
- **主题配置**: `_config.next.yml`
- **PWA 配置**: `_pwa.yml`
- **依赖管理**: `package.json`
- **GitHub Actions**: `.github/workflows/`

---

## 🎯 最佳实践

1. **定期更新**: 每 1-2 个月运行一次优化脚本
2. **备份配置**: 修改配置前先备份
3. **本地测试**: 部署前务必本地测试
4. **小步提交**: 频繁提交，便于回滚
5. **监控状态**: 定期检查 GitHub Actions 状态

---

## 🆘 故障排除

### 如果所有方法都失败：

1. **完全清理**:
   ```bash
   hexo clean
   rm -rf public/
   rm -rf .deploy_git/
   ```

2. **重装依赖**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install --legacy-peer-deps
   ```

3. **重新生成**:
   ```bash
   hexo generate
   ```

4. **运行优化脚本**:
   ```bash
   ./optimize-and-fix-blog.sh
   ```

---

## 📖 更多文档

- [详细修复报告](./BLOG_FIX_REPORT.md)
- [部署指南](./DEPLOY_GUIDE.md)
- [GitHub Actions 配置](./GITHUB_ACTIONS_SETUP_GUIDE.md)
- [AI 优化指南](./AI_OPTIMIZATION_GUIDE.md)

---

**最后更新**: 2026-03-19
