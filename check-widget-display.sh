#!/bin/bash
# ========================================
# 金融 AI 组件快速诊断与修复脚本
# 用途：自动检测并修复博客主页组件显示问题
# ========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 标题
echo ""
echo "========================================"
echo "🔍 金融 AI 组件诊断工具"
echo "========================================"
echo ""

# 检查项计数
CHECKS_PASSED=0
CHECKS_FAILED=0

# 1. 检查组件文件是否存在
print_info "检查 1: 验证组件文件..."
if [ -f "public/components/stock-chart-widget.html" ]; then
    STOCK_SIZE=$(du -h "public/components/stock-chart-widget.html" | cut -f1)
    print_success "股票预测组件存在 (大小：$STOCK_SIZE)"
    ((CHECKS_PASSED++))
else
    print_error "股票预测组件不存在！"
    ((CHECKS_FAILED++))
fi

if [ -f "public/components/crypto-dashboard-widget.html" ]; then
    CRYPTO_SIZE=$(du -h "public/components/crypto-dashboard-widget.html" | cut -f1)
    print_success "加密货币仪表板组件存在 (大小：$CRYPTO_SIZE)"
    ((CHECKS_PASSED++))
else
    print_error "加密货币仪表板组件不存在！"
    ((CHECKS_FAILED++))
fi

echo ""

# 2. 检查样式文件
print_info "检查 2: 验证样式文件..."
if [ -f "public/css/widget-components.css" ]; then
    CSS_SIZE=$(du -h "public/css/widget-components.css" | cut -f1)
    print_success "Widget 样式文件存在 (大小：$CSS_SIZE)"
    ((CHECKS_PASSED++))
else
    print_error "Widget 样式文件不存在！"
    ((CHECKS_FAILED++))
fi

echo ""

# 3. 检查 JavaScript 文件
print_info "检查 3: 验证 JavaScript 文件..."
if [ -f "public/js/widget-tabs.js" ]; then
    JS_SIZE=$(du -h "public/js/widget-tabs.js" | cut -f1)
    print_success "Tab 切换脚本存在 (大小：$JS_SIZE)"
    ((CHECKS_PASSED++))
else
    print_error "Tab 切换脚本不存在！"
    ((CHECKS_FAILED++))
fi

echo ""

# 4. 检查 index.html 中是否包含 widget-section
print_info "检查 4: 验证首页 HTML 结构..."
if grep -q "widget-section" "public/index.html"; then
    WIDGET_COUNT=$(grep -c "widget-section" "public/index.html")
    print_success "首页包含 Widget Section (出现 $WIDGET_COUNT 次)"
    ((CHECKS_PASSED++))
else
    print_error "首页未找到 Widget Section！"
    ((CHECKS_FAILED++))
fi

echo ""

# 5. 检查 index.html 中是否引用了 widget-tabs.js
print_info "检查 5: 验证 JavaScript 引用..."
if grep -q "widget-tabs.js" "public/index.html"; then
    print_success "首页已引用 widget-tabs.js"
    ((CHECKS_PASSED++))
else
    print_error "首页未引用 widget-tabs.js！"
    ((CHECKS_FAILED++))
fi

echo ""

# 6. 检查 index.html 中是否引用了 widget-components.css
print_info "检查 6: 验证 CSS 引用..."
if grep -q "widget-components.css" "public/index.html"; then
    print_success "首页已引用 widget-components.css"
    ((CHECKS_PASSED++))
else
    print_error "首页未引用 widget-components.css！"
    ((CHECKS_FAILED++))
fi

echo ""

# 7. 检查 iframe src 是否正确
print_info "检查 7: 验证 iframe 配置..."
if grep -q 'src="/components/stock-chart-widget.html"' "public/index.html"; then
    print_success "股票组件 iframe 路径正确"
    ((CHECKS_PASSED++))
else
    print_error "股票组件 iframe 路径错误！"
    ((CHECKS_FAILED++))
fi

if grep -q 'src="/components/crypto-dashboard-widget.html"' "public/index.html"; then
    print_success "加密货币组件 iframe 路径正确"
    ((CHECKS_PASSED++))
else
    print_error "加密货币组件 iframe 路径错误！"
    ((CHECKS_FAILED++))
fi

echo ""
echo "========================================"
echo "📊 检查结果汇总"
echo "========================================"
echo ""
print_success "通过：$CHECKS_PASSED 项"
if [ $CHECKS_FAILED -gt 0 ]; then
    print_error "失败：$CHECKS_FAILED 项"
else
    echo -e "失败：${CHECKS_FAILED} 项"
fi

echo ""

# 根据检查结果给出建议
if [ $CHECKS_FAILED -eq 0 ]; then
    print_success "所有检查项通过！组件应该正常显示。"
    echo ""
    echo "💡 如果仍然看不到组件，请尝试："
    echo "   1. 清除浏览器缓存（Ctrl+Shift+R 或 Cmd+Shift+R）"
    echo "   2. 打开浏览器控制台查看是否有 JavaScript 错误"
    echo "   3. 直接访问组件 URL 测试："
    echo "      - https://088.us.ci/components/stock-chart-widget.html"
    echo "      - https://088.us.ci/components/crypto-dashboard-widget.html"
    echo ""
else
    print_warning "发现 $CHECKS_FAILED 项问题，需要修复。"
    echo ""
    read -p "是否要重新生成并部署？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "开始重新生成..."
        hexo clean
        hexo generate
        print_success "生成完成！"
        echo ""
        read -p "是否立即部署？(y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "开始部署..."
            hexo deploy
            print_success "部署完成！"
        fi
    fi
fi

echo ""
echo "========================================"
echo "📖 详细诊断指南请查看:"
echo "   博客主页组件显示问题诊断指南.md"
echo "========================================"
echo ""
