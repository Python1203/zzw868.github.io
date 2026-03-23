# GitHub Actions 配置指南

本文档介绍如何配置 GitHub Secrets 以启用自动 AI 创作和部署功能。

---

## 🔑 必须配置的 Secrets

### 1. AI_API_KEY（必需）

AI 模型的 API 密钥，用于驱动 AI 创作。

#### 获取方式：

**选项 A: OpenAI GPT-4**
```bash
AI_API_KEY=sk-usxxxxxxxxxxxxxxxx
AI_BASE_URL=https://api.openai.com/v1
```

**选项 B: 通义千问（推荐国内用户）**
1. 访问 https://dashscope.console.aliyun.com/
2. 注册账号并创建 API Key
3. 复制 Key 值
```bash
AI_API_KEY=sk-xxxxxxxxxxxxxxxx
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**选项 C: 深度求索（性价比高）**
1. 访问 https://platform.deepseek.com/
2. 注册并获取 API Key（新用户赠送额度）
```bash
AI_API_KEY=sk-xxxxxxxxxxxxxxxx
AI_BASE_URL=https://api.deepseek.com/v1
```

### 2. GH_TOKEN（必需）

GitHub Personal Access Token，用于推送代码和部署。

#### 获取步骤：

1. **访问 GitHub Settings**
   - 点击右上角头像 → Settings
   - 或访问 https://github.com/settings/tokens

2. **生成新 Token**
   - 点击 "Generate new token (classic)"
   - 或 "Generate new token" → "Generate new token (classic)"

3. **配置权限（重要！）**
   勾选以下权限：
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `admin:org` (如果仓库在 Organization 下)

4. **生成并复制**
   - 点击 "Generate token"
   - ⚠️ **立即复制 Token**（只显示一次！）
   - 格式如：`ghp_xxxxxxxxxxxxxxxxxxxx`

5. **添加到 Secrets**
   ```
   Name: GH_TOKEN
   Value: ghp_xxxxxxxxxxxxxxxxxxxx
   ```

---

## ⚙️ 可选的 Secrets

### 3. AI_BASE_URL（可选）

AI 模型的 API 基础 URL，如果使用 OpenAI 可不配置。

```bash
# 通义千问
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 百度文心
AI_BASE_URL=https://qianfan.baidubce.com/v2

# 深度求索
AI_BASE_URL=https://api.deepseek.com/v1
```

### 4. BDU_API_TOKEN（可选）

百度站长平台 API Token，用于 SEO 自动提交。

获取方式见：[SEO_SUBMIT_GUIDE.md](SEO_SUBMIT_GUIDE.md)

### 5. BING_API_KEY（可选）

Bing Webmaster Tools API Key。

获取方式见：[SEO_SUBMIT_GUIDE.md](SEO_SUBMIT_GUIDE.md)

---

## 📝 添加 Secrets 的完整步骤

### Step-by-Step

1. **打开仓库 Settings**
   ```
   https://github.com/zzw868/zzw868.github.io/settings/secrets/actions
   ```

2. **点击 "New repository secret"**

3. **填写 Secret 信息**
   
   **添加 AI_API_KEY:**
   ```
   Name: AI_API_KEY
   Value: sk-your-api-key-here
   ```
   
   **添加 GH_TOKEN:**
   ```
   Name: GH_TOKEN
   Value: ghp-your-token-here
   ```
   
   **添加 AI_BASE_URL（如果需要）:**
   ```
   Name: AI_BASE_URL
   Value: https://dashscope.aliyuncs.com/compatible-mode/v1
   ```

4. **点击 "Add secret" 保存**

5. **重复步骤 2-4** 添加所有必需的 Secrets

---

## ✅ 验证配置

### 方法 1: 手动触发工作流

1. 访问 https://github.com/zzw868/zzw868.github.io/actions
2. 选择 "Global Finance AI Blog" 工作流
3. 点击 "Run workflow" 按钮
4. 使用默认参数运行
5. 等待执行完成（约 2-3 分钟）
6. 检查是否生成新文章

### 方法 2: 查看环境变量

在工作流中添加调试步骤：

```yaml
- name: Debug Secrets
  run: |
    echo "AI_API_KEY exists: ${{ secrets.AI_API_KEY != '' }}"
    echo "GH_TOKEN exists: ${{ secrets.GH_TOKEN != '' }}"
```

---

## 🐛 常见问题排查

### 问题 1: 提示 "Permission denied" 或 "Authentication failed"

**原因：** GH_TOKEN 未配置或权限不足

**解决：**
1. 检查是否添加了 `GH_TOKEN` Secret
2. 确认 Token 有以下权限：
   - `repo` (必需)
   - `workflow` (必需)
3. 重新生成 Token 并更新 Secret

### 问题 2: AI_API_KEY 无效

**检查：**
```bash
# 本地测试
export AI_API_KEY='sk-xxx'
python scripts/ai_writer.py --count 1
```

如果本地成功但 GitHub Actions 失败：
1. 检查 Secret 名称是否正确（区分大小写）
2. 确认没有多余的空格
3. 查看 Actions 日志中的具体错误信息

### 问题 3: 工作流不执行

**检查清单：**
- [ ] Actions 是否启用（Settings → Actions）
- [ ] 工作流文件语法是否正确
- [ ] 是否有 `.github/workflows/finance_auto_blog.yml` 文件
- [ ] 查看 Actions 标签页是否有红色警告

### 问题 4: 定时任务不触发

**可能原因：**
- GitHub Actions 调度可能有延迟（正常现象）
- 仓库长时间不活动可能被暂停

**解决：**
- 手动触发一次激活
- 定期有 commit 活动

---

## 🎯 最佳实践

### 安全建议

1. **不要硬编码 Token**
   ```yaml
   # ❌ 错误做法
   env:
     AI_API_KEY: sk-xxxxx  # 绝对不要这样写！
   
   # ✅ 正确做法
   env:
     AI_API_KEY: ${{ secrets.AI_API_KEY }}
   ```

2. **定期轮换 Token**
   - 每 3-6 个月重新生成 GH_TOKEN
   - 旧 Token 失效后及时更新 Secret

3. **最小权限原则**
   - 只授予必要的权限
   - 避免使用 `admin` 级别权限

### 成本优化

1. **控制生成频率**
   - 定时任务：每天 1 篇足够
   - 批量生成时限制数量（最多 5 篇/次）

2. **选择合适的模型**
   - 日常文章：使用国产模型（便宜、快速）
   - 深度报告：使用 GPT-4（质量高）

3. **利用免费额度**
   - DeepSeek 新用户赠送 ¥5
   - 通义千问有一定免费额度

---

## 📊 监控与告警

### 查看执行历史

1. 访问 https://github.com/zzw868/zzw868.github.io/actions
2. 点击 "Global Finance AI Blog"
3. 查看最近的运行记录

### 设置邮件通知

GitHub 会自动发送邮件通知：
- 工作流失败时
- 长时间运行的任务完成时

如需更多通知，可配置：
- Slack 集成
- Discord Webhook
- 企业微信机器人

---

## 🔗 相关资源

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [Scheduled workflows](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule)
- [Managing secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)
- [crontab 表达式生成器](https://crontab.guru/) - 测试你的 cron 表达式

---

## 🆘 获取帮助

遇到问题时的检查顺序：

1. **查看 Secrets** - 确认已正确配置
2. **查看日志** - Actions → 对应运行 → 查看详细日志
3. **本地测试** - 在本地运行脚本验证
4. **搜索 Issue** - 查看是否有类似问题
5. **手动触发** - 排除定时任务的延迟问题

---

最后更新：2026-03-17
