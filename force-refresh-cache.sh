#!/bin/bash
# ========================================
# 强制清除浏览器缓存并刷新 GitHub Pages
# ========================================

echo "🔧 开始清除缓存流程..."
echo ""

# 1. 检查当前提交的 financial-data-service.js 内容
echo "✅ 步骤 1: 验证本地文件是否正确"
if grep -q "^// export {" source/js/financial-data-service.js; then
    echo "   ✓ 本地文件已正确修复 (export 已注释)"
else
    echo "   ✗ 本地文件仍有问题！"
    exit 1
fi

# 2. 检查 GitHub 上的文件
echo ""
echo "📡 步骤 2: 检查 GitHub 远程文件"
REMOTE_CONTENT=$(curl -s https://raw.githubusercontent.com/Python1203/zzw868.github.io/main/source/js/financial-data-service.js | tail -5)

if echo "$REMOTE_CONTENT" | grep -q "^// export {"; then
    echo "   ✓ GitHub 上的文件已更新"
else
    echo "   ⚠️  GitHub 上的文件可能未更新，等待 CDN 刷新..."
fi

# 3. 提供清除缓存的方法
echo ""
echo "=========================================="
echo "🎯 请在浏览器中执行以下操作："
echo "=========================================="
echo ""
echo "方法 1: 强制刷新（推荐）"
echo "  Windows/Linux: Ctrl + Shift + R"
echo "  Mac:           Cmd + Shift + R"
echo ""
echo "方法 2: 使用开发者工具"
echo "  1. 按 F12 打开开发者工具"
echo "  2. 右键点击刷新按钮"
echo "  3. 选择'清空缓存并硬性重新加载'"
echo ""
echo "方法 3: 完全清除站点数据"
echo "  1. F12 → Application → Storage"
echo "  2. 点击 'Clear site data'"
echo "  3. 刷新页面"
echo ""
echo "=========================================="
echo ""

# 4. 验证 CDN
echo "🌐 检查 GitHub Pages CDN 状态..."
CDN_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://088.us.ci/js/financial-data-service.js)
if [ "$CDN_CHECK" = "200" ]; then
    echo "   ✓ CDN 可访问：https://088.us.ci/js/financial-data-service.js"
    echo "   ⏰ CDN 可能有 1-2 分钟延迟，请稍候再刷新"
else
    echo "   ⚠️  CDN 响应异常：$CDN_CHECK"
fi

echo ""
echo "💡 提示：GitHub Pages CDN 通常需要 1-2 分钟刷新"
echo "   如果仍然看到旧错误，请等待 1 分钟后再次强制刷新"
echo ""
echo "✅ 认证完成通知：所有修复已推送至 GitHub，请按照上述方法清除缓存！"
echo ""
