#!/bin/bash
# ========================================
# 实时监测 CDN 文件更新状态
# ========================================

echo "🔍 开始检查 CDN 缓存状态..."
echo ""

MAX_ATTEMPTS=10
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "第 $ATTEMPT 次检查 ($(date '+%H:%M:%S'))"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 检查 CDN 上的文件
    CDN_CONTENT=$(curl -s "https://088.us.ci/js/financial-data-service.js" 2>/dev/null)
    
    if echo "$CDN_CONTENT" | grep -q "^// export {"; then
        echo ""
        echo "✅ 成功！CDN 文件已更新！"
        echo ""
        echo "📊 文件最后几行内容："
        echo "$CDN_CONTENT" | tail -5
        echo ""
        echo "💡 现在请在浏览器中按 Ctrl+Shift+R (或 Cmd+Shift+R) 强制刷新！"
        exit 0
    else
        echo "⏳ CDN 文件仍未更新，当前包含："
        echo "$CDN_CONTENT" | grep "export {" || echo "(未找到 export 语句)"
        echo ""
        echo "⏰ 等待 30 秒后再次检查..."
        echo ""
        sleep 30
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
done

echo ""
echo "⚠️  已达到最大检查次数 ($MAX_ATTEMPTS 次)"
echo "💡 建议："
echo "   1. 访问 https://github.com/Python1203/zzw868.github.io/actions"
echo "   2. 查看最新的 'Build & Deploy' 工作流是否成功"
echo "   3. 如果失败，请检查 GitHub Actions 日志"
echo ""
