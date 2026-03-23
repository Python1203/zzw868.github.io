# 🔐 GitHub Secrets 配置指南

本指南将详细教你如何配置 GitHub Actions 所需的环境变量（Secrets）。

---

## 📋 需要配置的 Secrets

| Secret 名称 | 用途 | 是否必需 | 示例值 |
|------------|------|---------|--------|
| `AI_API_KEY` | AI 模型 API 密钥 | ✅ 必需 | `sk-xxxxxxxx` |
| `GH_TOKEN` | GitHub 个人访问令牌 | ✅ 必需 | `ghp_xxxxxx` |
| `AI_BASE_URL` | AI API 基础 URL | ❌ 可选 | `https://api.openai.com/v1` |

---

## 🚀 快速配置步骤

### Step 1: 打开 Secrets 设置页面

**方式 A: 直接访问链接**
```
https://github.com/zzw868/zzw868.github.io/settings/secrets/actions
```

**方式 B: 手动导航**
1. 打开你的仓库：https://github.com/zzw868/zzw868.github.io
2. 点击顶部导航栏的 **Settings**（设置）
3. 左侧菜单找到 **Secrets and variables** → **Actions**

---

### Step 2: 获取 AI_API_KEY

#### 选项 A: OpenAI GPT-4

1. 访问 https://platform.openai.com/api-keys
2. 登录或注册 OpenAI 账号
3. 点击 "Create new secret key"
4. 复制生成的 Key（格式：`sk-proj-xxxxxxxx` 或 `sk-usxxxxxxxx`）
5. ⚠️ **立即保存**，只显示一次！

#### 选项 B: 通义千问（阿里云）

1. 访问 https://dashscope.console.aliyun.com/apiKey
2. 使用阿里云账号登录
3. 点击 "创建新的 API-Key"
4. 复制 Key（格式：`sk-xxxxxxxx`）

#### 选项 C: 深度求索（DeepSeek）

1. 访问 https://platform.deepseek.com/api_keys
2. 注册账号（新用户赠送 ¥5 额度）
3. 创建 API Key
4. 复制 Key（格式：`sk-xxxxxxxx`）

#### 选项 D: 百度文心一言

1. 访问 https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application
2. 创建应用
3. 获取 API Key 和 Secret Key

---

### Step 3: 获取 GH_TOKEN（GitHub Personal Access Token）

#### 详细步骤：

1. **访问 Token 设置页面**
   ```
   https://github.com/settings/tokens
   ```
   或：头像 → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **选择 Token 类型**
   - 点击 **"Generate new token"**
   - 选择 **"Generate new token (classic)"**

3. **填写 Token 信息**
   
   **Note（备注）**: 
   ```
   Hexo Blog Auto Deploy - zzw868.github.io
   ```
   
   **Expiration（过期时间）**: 
   - 推荐：`No expiration`（永久）
   - 或选择 90 天（更安全，需定期更新）

4. **勾选权限（重要！）**
   
   必须勾选以下权限：
   - ✅ **`repo`** (Full control of private repositories)
     - 展开确保包含：`repo:status`, `repo_deployment`, `public_repo`, `repo:invite`
   - ✅ **`workflow`** (Update GitHub Action workflows)
   
   可选权限（如果需要）：
   - `admin:org` (如果仓库在 Organization 下)

5. **生成 Token**
   - 滚动到页面底部
   - 点击 **"Generate token"**

6. **复制 Token**
   - ⚠️ **立即复制显示的 Token！**
   - 格式如：`ghp_1a2b3c4d5e6f7g8h9i0j...`
   - 🔒 **只显示一次，刷新后无法再查看！**

---

### Step 4: 添加 Secrets 到 GitHub

现在回到仓库的 Secrets 设置页面：

#### 添加 AI_API_KEY

1. 点击 **"New repository secret"** 按钮

2. 填写信息：
   ```
   Name: AI_API_KEY
   Value: sk-your-actual-api-key-here
   ```

3. 点击 **"Add secret"** 保存

#### 添加 GH_TOKEN

1. 再次点击 **"New repository secret"**

2. 填写信息：
   ```
   Name: GH_TOKEN
   Value: ghp_your-personal-access-token-here
   ```

3. 点击 **"Add secret"** 保存

#### （可选）添加 AI_BASE_URL

如果使用非 OpenAI 模型：

1. 点击 **"New repository secret"**

2. 填写信息：
   ```
   Name: AI_BASE_URL
   Value: https://dashscope.aliyuncs.com/compatible-mode/v1
   ```
   
   或其他模型的 URL：
   - DeepSeek: `https://api.deepseek.com/v1`
   - 百度文心：`https://qianfan.baidubce.com/v2`

3. 点击 **"Add secret"** 保存

---

## ✅ 验证配置

### 方法 1: 查看已配置的 Secrets

回到 Secrets 页面，应该能看到：

```
Secrets (3)
├─ AI_API_KEY      (Added just now)
├─ GH_TOKEN        (Added just now)
└─ AI_BASE_URL     (Added just now) [Optional]
```

⚠️ **注意：** 出于安全考虑，你只能看到 Secret 的名称，看不到具体值。

### 方法 2: 测试工作流

1. 访问 Actions 页面：
   ```
   https://github.com/zzw868/zzw868.github.io/actions
   ```

2. 选择 **"Global Finance AI Blog"** 工作流

3. 点击 **"Run workflow"**

4. 使用默认参数，点击 **"Run workflow"**

5. 等待执行完成（约 2-3 分钟）

6. 检查：
   - ✅ 绿色勾号表示成功
   - ❌ 红色叉号表示失败，点击查看日志

### 方法 3: 在工作流中添加调试步骤

临时修改 `.github/workflows/finance_auto_blog.yml`，添加：

```yaml
- name: Debug Secrets
  run: |
    echo "Checking secrets..."
    if [ -n "${{ secrets.AI_API_KEY }}" ]; then
      echo "✅ AI_API_KEY is set"
    else
      echo "❌ AI_API_KEY is NOT set"
    fi
    
    if [ -n "${{ secrets.GH_TOKEN }}" ]; then
      echo "✅ GH_TOKEN is set"
    else
      echo "❌ GH_TOKEN is NOT set"
    fi
```

运行工作流查看输出。

---

## 🐛 常见问题排查

### 问题 1: "Error: Invalid API Key"

**可能原因：**
- API Key 复制时多了空格或换行
- API Key 已过期或被撤销
- 使用了错误的 Base URL

**解决方法：**
1. 重新复制 API Key（确保没有多余字符）
2. 删除旧的 Secret，重新添加
3. 确认 AI_BASE_URL 是否正确

### 问题 2: "Permission denied" 或 "Authentication failed"

**可能原因：**
- GH_TOKEN 未配置
- Token 权限不足
- Token 已过期

**解决方法：**
1. 检查是否添加了 `GH_TOKEN` Secret
2. 重新生成 Token，确保勾选了：
   - ✅ `repo` (全部子权限)
   - ✅ `workflow`
3. 更新 Secret

### 问题 3: Secret 名称不匹配

**症状：** 工作流中读取不到 Secret

**检查：**
- Secret 名称必须**完全一致**（区分大小写）
- `AI_API_KEY` ≠ `Ai_Api_Key` ≠ `ai_api_key`

**解决：** 删除错误的 Secret，重新添加正确名称的

### 问题 4: "Repository not found" 或 "404 Not Found"

**可能原因：**
- GH_TOKEN 权限不足
- 仓库是私有的但 Token 没有 `repo` 权限

**解决：** 重新生成 Token，确保勾选 `repo` 全部权限

---

## 🔒 安全最佳实践

### 1. 不要泄露 Secrets

❌ **绝对不要：**
```yaml
# 错误示例 - 硬编码 Secret
env:
  AI_API_KEY: sk-xxxxx  # 这是严重的安全漏洞！

# 错误示例 - 打印 Secret
run: echo $AI_API_KEY  # 会暴露到日志中！
```

✅ **正确做法：**
```yaml
# 正确示例 - 使用 GitHub Secrets
env:
  AI_API_KEY: ${{ secrets.AI_API_KEY }}

# 只验证是否存在，不打印具体值
run: |
  if [ -n "${{ secrets.AI_API_KEY }}" ]; then
    echo "API Key is configured"
  fi
```

### 2. 定期轮换 Token

建议每 **3-6 个月** 重新生成一次：

1. 生成新的 Token
2. 更新 GitHub Secret
3. 测试工作流
4. 删除旧的 Token

### 3. 最小权限原则

只授予必要的权限：
- 博客部署只需要 `repo` 和 `workflow`
- 不要给 `admin` 权限（除非必要）

### 4. 监控使用情况

定期检查：
- https://github.com/settings/tokens
- 查看哪些 Token 在使用
- 删除不再使用的 Token

---

## 📊 完整配置示例

### 最终 Secrets 列表

配置完成后，你的 Secrets 页面应该显示：

```
Repository secrets

Name              Last updated
─────────────────────────────────────
AI_API_KEY        Updated 2 minutes ago
GH_TOKEN          Updated 2 minutes ago  
AI_BASE_URL       Updated 2 minutes ago (optional)
```

### 工作流中的使用

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Use AI API Key
        env:
          AI_API_KEY: ${{ secrets.AI_API_KEY }}
          AI_BASE_URL: ${{ secrets.AI_BASE_URL }}
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
        run: |
          python scripts/ai_writer.py
```

---

## 🎯 快速检查清单

配置前准备：
- [ ] OpenAI/通义千问/DeepSeek 账号
- [ ] GitHub 账号已登录
- [ ] 浏览器可以访问 GitHub

配置过程：
- [ ] 获取了 AI_API_KEY
- [ ] 生成了 GH_TOKEN
- [ ] GH_TOKEN 勾选了 `repo` 和 `workflow` 权限
- [ ] 复制了两个 Key（保存到安全位置）

添加到 GitHub：
- [ ] 打开了正确的仓库 Settings
- [ ] 导航到 Secrets and variables → Actions
- [ ] 添加了 `AI_API_KEY` Secret
- [ ] 添加了 `GH_TOKEN` Secret
- [ ] （可选）添加了 `AI_BASE_URL` Secret

验证：
- [ ] 在 Secrets 页面能看到 3 个 Secret
- [ ] 手动触发了一次工作流
- [ ] 工作流执行成功（绿色勾号）
- [ ] 生成了新的文章文件
- [ ] 成功部署到了 GitHub Pages

---

## 🔗 相关资源

- [GitHub Secrets 官方文档](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [Personal Access Tokens 文档](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [通义千问 API](https://help.aliyun.com/zh/dashscope/)
- [DeepSeek API](https://platform.deepseek.com/)

---

## 🆘 需要帮助？

如果遇到无法解决的问题：

1. **查看详细日志**
   - Actions → 对应运行记录 → 点击查看详情
   - 查看具体错误信息

2. **检查 Secret 名称**
   - 确保拼写完全正确
   - 区分大小写

3. **本地测试**
   ```bash
   export AI_API_KEY='sk-xxx'
   python scripts/ai_writer.py --count 1
   ```

4. **查阅文档**
   - [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
   - [AI_WRITER_GUIDE.md](../../scripts/AI_WRITER_GUIDE.md)

---

**祝你配置顺利！** 🎉

配置完成后，你的博客将每天自动生成并部署 AI 文章！

最后更新：2026-03-17
