# 📦 博客部署指南 - 解决首页和目录不显示更新内容

## 🔍 问题原因

博客文章已经生成在 `.deploy_git` 目录中，但需要推送到 GitHub 的 `gh-pages` 分支才能在网站上显示。

## ✅ 快速解决方案（3 选 1）

### 方式 1: 使用自动部署脚本（最简单）

```bash
./quick-deploy.sh
```

### 方式 2: 手动部署

```bash
cd .deploy_git
git add -A
git commit -m "deploy update"
git push origin gh-pages
```

### 方式 3: 使用现有脚本

```bash
./emergency-deploy.sh
```

## 🔧 配置 SSH Key（推荐，一劳永逸）

```bash
# 1. 生成 SSH Key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub

# 3. 复制到 GitHub
# https://github.com/settings/keys -> New SSH key
```

## 📊 验证步骤

### 1. 检查本地文件

```bash
ls -lh .deploy_git/index.html
grep "financial-report" .deploy_git/index.html | head -3
```

### 2. 检查 GitHub 仓库

访问：https://github.com/Python1203/zzw868.github.io/tree/gh-pages

### 3. 检查网站

访问：https://zzw868.github.io

**注意**: GitHub Pages 可能需要 1-2 分钟才能生效。

## 🐛 常见问题

### Q: 推送失败，提示权限错误

**解决**:
```bash
# 改用 SSH 方式
git remote set-url origin git@github.com:Python1203/zzw868.github.io.git
```

### Q: 推送成功但网站没更新

**解决**:
1. 等待 1-2 分钟（GitHub 缓存）
2. Ctrl+F5 强制刷新浏览器
3. 检查 gh-pages 分支是否已更新

---

*最后更新：2026-03-19*
