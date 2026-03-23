#!/bin/bash
# GitHub Actions 配置检查脚本

echo "🔍 GitHub Actions 配置检查"
echo "=========================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查计数器
PASS=0
WARN=0
FAIL=0

# 1. 检查 template.html 是否在根目录
echo "📄 检查 template.html..."
if [ -f "template.html" ]; then
    echo -e "${GREEN}✅ template.html 存在${NC}"
    ((PASS++))
else
    echo -e "${RED}❌ template.html 不存在${NC}"
    echo "   提示：template.html 必须在仓库根目录"
    ((FAIL++))
fi
echo ""

# 2. 检查 pages 目录
echo "📁 检查 pages 目录..."
if [ -d "pages" ]; then
    HTML_COUNT=$(find pages -name "*.html" | wc -l)
    if [ "$HTML_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ pages 目录存在，包含 $HTML_COUNT 个 HTML 文件${NC}"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️  pages 目录存在但没有 HTML 文件${NC}"
        ((WARN++))
    fi
else
    echo -e "${YELLOW}⚠️  pages 目录不存在（Actions 会自动创建）${NC}"
    ((WARN++))
fi
echo ""

# 3. 检查 GitHub Actions 工作流文件
echo "🔧 检查 GitHub Actions 配置文件..."
if [ -f ".github/workflows/main.yml" ] || [ -f ".github/workflows/auto_generate_nav.yml" ]; then
    echo -e "${GREEN}✅ 工作流文件存在${NC}"
    ((PASS++))
    
    # 显示找到的工作流文件
    if [ -f ".github/workflows/main.yml" ]; then
        echo "   - .github/workflows/main.yml"
    fi
    if [ -f ".github/workflows/auto_generate_nav.yml" ]; then
        echo "   - .github/workflows/auto_generate_nav.yml"
    fi
else
    echo -e "${RED}❌ 工作流文件不存在${NC}"
    echo "   提示：确保 .github/workflows/ 目录中有 .yml 文件"
    ((FAIL++))
fi
echo ""

# 4. 检查 Git 状态
echo "📊 检查 Git 状态..."
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 这是一个 Git 仓库${NC}"
    ((PASS++))
    
    # 检查是否有未提交的变更
    CHANGED=$(git status --porcelain)
    if [ -z "$CHANGED" ]; then
        echo -e "${GREEN}✅ 没有未提交的变更${NC}"
    else
        echo -e "${YELLOW}⚠️  有未提交的变更:${NC}"
        echo "$CHANGED" | head -5
        if [ $(echo "$CHANGED" | wc -l) -gt 5 ]; then
            echo "... 更多文件未显示"
        fi
        ((WARN++))
    fi
    
    # 检查远程仓库
    REMOTE=$(git remote get-url origin 2>/dev/null)
    if [ -n "$REMOTE" ]; then
        echo -e "${GREEN}✅ 远程仓库已配置：$REMOTE${NC}"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️  未配置远程仓库${NC}"
        ((WARN++))
    fi
else
    echo -e "${RED}❌ 这不是一个 Git 仓库${NC}"
    echo "   提示：需要初始化为 Git 仓库并推送到 GitHub"
    ((FAIL++))
fi
echo ""

# 5. 检查 index.html（如果存在）
echo "📑 检查 index.html..."
if [ -f "index.html" ]; then
    echo -e "${GREEN}✅ index.html 已存在${NC}"
    echo "   注意：这个文件将由 Actions 自动生成，可以删除"
    ((PASS++))
else
    echo -e "${YELLOW}ℹ️  index.html 不存在（将由 Actions 生成）${NC}"
    ((PASS++))
fi
echo ""

# 6. 总结
echo "=========================="
echo "📊 检查结果汇总:"
echo "=========================="
echo -e "${GREEN}✅ 通过：$PASS${NC}"
echo -e "${YELLOW}⚠️  警告：$WARN${NC}"
echo -e "${RED}❌ 失败：$FAIL${NC}"
echo ""

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}❌ 配置不完整，请先修复上述问题${NC}"
    echo ""
    echo "📖 详细配置指南请查看：GITHUB_ACTIONS_SETUP_GUIDE.md"
    exit 1
elif [ $WARN -gt 0 ]; then
    echo -e "${YELLOW}⚠️  配置基本正确，但有一些注意事项${NC}"
    echo ""
    echo "下一步："
    echo "1. 将 HTML 文件放入 pages/ 目录"
    echo "2. 提交并推送到 GitHub"
    echo "3. 在 GitHub 上配置 Actions 权限和 Pages"
    echo ""
    echo "📖 详细指南：GITHUB_ACTIONS_SETUP_GUIDE.md"
else
    echo -e "${GREEN}✅ 所有检查通过！可以推送到 GitHub 了${NC}"
    echo ""
    echo "推送命令："
    echo "  git add ."
    echo "  git commit -m 'Add auto navigation system'"
    echo "  git push origin main"
    echo ""
    echo "📖 详细指南：GITHUB_ACTIONS_SETUP_GUIDE.md"
fi

echo ""
echo "=========================="
