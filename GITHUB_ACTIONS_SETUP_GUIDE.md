# 🚀 GitHub Actions 自动导航 - 快速配置指南

## 📋 完整配置流程（5 分钟搞定）

### 第一步：准备文件结构 ✅

#### 1. 创建 pages 目录
```bash
mkdir pages
```

#### 2. 将 HTML 文件移动到 pages
```bash
# 移动所有 HTML 文件到 pages 目录
mv *.html pages/

# 但保留 template.html 在根目录
mv template.html ../
cd ..
```

**最终结构：**
```
你的仓库/
├── .github/workflows/
│   └── main.yml          ← GitHub Actions 配置文件
├── pages/
│   ├── page1.html        ← 你的 HTML 文件
│   ├── page2.html
│   └── ... (更多页面)
├── template.html         ← 模板文件（重要！）
└── index.html           ← 自动生成（不需要手动创建）
```

---

### 第二步：GitHub 仓库设置 🔧

#### 1️⃣ 开启 Workflow 权限

**路径：** Settings → Actions → General

**步骤：**
1. 打开你的 GitHub 仓库
2. 点击 **Settings** 标签
3. 左侧菜单选择 **Actions**
4. 点击 **General**
5. 向下滚动到 **Workflow permissions**
6. 选择 **Read and write permissions**
7. 勾选 "Allow GitHub Actions to create and approve pull requests"
8. 点击 **Save**

**为什么需要？**
- ✅ Actions 需要写入权限来提交生成的 `index.html`
- ✅ 没有此权限会导致部署失败

![Workflow Permissions](https://docs.github.com/assets/cb-44343/images/help/repository/actions-workflow-permissions-write.png)

---

#### 2️⃣ 启用 GitHub Pages

**路径：** Settings → Pages → Build and deployment

**步骤：**
1. 在 Settings 页面，左侧菜单选择 **Pages**
2. 找到 **Build and deployment** 部分
3. **Source** 选择 **GitHub Actions**
4. 点击 **Save**

**注意：**
- ⚠️ 不要选择 Deploy from a branch
- ✅ 必须选择 GitHub Actions
- 🎯 这样 Actions 才能控制部署

![GitHub Pages Source](https://docs.github.com/assets/cb-12345/images/help/repository/pages-source-actions.png)

---

### 第三步：推送到 GitHub 🚀

#### 1. 添加所有文件到 Git
```bash
git add .
```

#### 2. 提交
```bash
git commit -m "Add auto navigation system with GitHub Actions"
```

#### 3. 推送到 GitHub
```bash
git push origin main
```

---

### 第四步：验证 Actions 运行 👀

#### 1. 访问 Actions 页面
```
https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

#### 2. 查看工作流状态
- 应该看到 **"Auto Generate Index"** 正在运行
- 点击进去查看详细日志

#### 3. 预期输出
```
✅ 找到 30 个 HTML 文件:
   - Page1: pages/page1.html
   - Page2: pages/page2.html
   ...

✅ 成功生成 index.html
📊 包含 30 个页面
```

---

### 第五步：检查部署结果 ✨

#### 1. 等待完成
- 通常需要 30-60 秒
- 看到绿色勾表示成功

#### 2. 访问 GitHub Pages
```
https://YOUR_USERNAME.github.io/YOUR_REPO/
```

#### 3. 验证功能
- ✅ 左侧菜单栏显示所有页面
- ✅ 点击菜单项加载对应内容
- ✅ iframe 正确显示页面

---

## 🔍 故障排除

### ❌ 问题 1: Actions 无法提交代码

**错误信息：**
```
Error: Permission denied
```

**解决方案：**
1. 检查 Settings → Actions → General
2. 确认选择了 **Read and write permissions**
3. 重新推送代码触发新的 workflow

---

### ❌ 问题 2: Pages 显示 404

**原因：**
- Pages 还没有正确配置

**解决方案：**
1. Settings → Pages
2. Source 必须选择 **GitHub Actions**
3. 等待 2-3 分钟

---

### ❌ 问题 3: template.html 找不到

**错误信息：**
```
❌ 模板文件不存在：template.html
```

**解决方案：**
```bash
# 确保 template.html 在根目录
ls -la template.html

# 如果不在，从 pages 移回来
mv pages/template.html ./
git add template.html
git commit -m "Move template.html to root"
git push
```

---

### ❌ 问题 4: 没有扫描到 HTML 文件

**错误信息：**
```
⚠️  未找到任何 HTML 文件
```

**解决方案：**
```bash
# 检查文件是否在 pages 目录
ls -la pages/*.html

# 如果没有，移动进去
mkdir -p pages
mv *.html pages/
git add pages/
git commit -m "Move HTML files to pages directory"
git push
```

---

## 📊 完整配置检查清单

在推送之前，请确认：

- [ ] **文件结构正确**
  - [ ] `template.html` 在根目录
  - [ ] 所有 HTML 文件在 `pages/` 目录
  - [ ] `.github/workflows/main.yml` 存在

- [ ] **GitHub 设置正确**
  - [ ] Settings → Actions → General → Read and write permissions ✅
  - [ ] Settings → Pages → Source → GitHub Actions ✅

- [ ] **Git 操作正确**
  - [ ] `git add .` 添加了所有文件
  - [ ] `git commit -m "..."` 提交了变更
  - [ ] `git push origin main` 推送到正确的分支

---

## 🎯 预期结果

### Actions 运行日志示例

```yaml
Run Auto Generate Index
📁 正在扫描目录：pages
✅ 找到 30 个 HTML 文件:
   - Page1: pages/page1.html
   - Page2: pages/page2.html
   - Page3: pages/page3.html
   ...

✅ 成功生成 index.html
📊 包含 30 个页面

✅ index.html 生成成功
-rw-r--r-- 1 runner docker 15K Mar 19 15:30 index.html

Auto-generate index.html [skip ci]
Deploying to gh-pages branch...
Deployment completed!
```

### GitHub Pages 最终效果

访问 `https://YOUR_USERNAME.github.io/YOUR_REPO/`

**看到的内容：**
- ✅ 左侧渐变菜单栏
- ✅ 30 个页面名称列表
- ✅ 右侧 iframe 显示第一个页面
- ✅ 点击菜单切换页面
- ✅ 响应式设计（移动端适配）

---

## 💡 高级技巧

### 1. 手动触发工作流

如果自动触发失败，可以手动运行：

1. 访问 https://github.com/YOUR_USERNAME/YOUR_REPO/actions
2. 点击 **"Auto Generate Index"** 工作流
3. 点击 **"Run workflow"** 按钮
4. 选择分支（通常是 main）
5. 点击 **"Run workflow"**

### 2. 批量重命名文件

如果文件名不规范：

```bash
cd pages

# 批量替换空格为连字符
for file in *.html; do
    new_name=$(echo "$file" | tr ' ' '-')
    if [ "$file" != "$new_name" ]; then
        mv "$file" "$new_name"
    fi
done

git add .
git commit -m "Normalize filenames"
git push
```

### 3. 添加新页面

只需简单三步：

```bash
# 1. 创建新页面
cat > pages/new-page.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>新页面</title></head>
<body><h1>这是新页面</h1></body>
</html>
EOF

# 2. 提交
git add pages/new-page.html
git commit -m "Add new page"

# 3. 推送（自动更新导航）
git push
```

---

## 🎉 完成！

现在你已经完成了所有配置：

1. ✅ 文件存放在正确的目录
2. ✅ GitHub Actions 权限已开启
3. ✅ Pages 已配置使用 Actions
4. ✅ 代码已推送到 GitHub
5. ✅ Actions 自动运行并部署

**享受自动化的便利吧！** 🚀

每次添加新页面时，Actions 会自动：
- 扫描 pages 目录
- 更新 index.html
- 部署到 GitHub Pages
- 无需手动干预！

---

**最后检查：**
- 访问你的 GitHub Pages 链接
- 确认所有页面都能正常访问
- 分享你的自动化成果！🎊
