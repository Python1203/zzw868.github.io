#!/bin/bash
# ============================================================================
# 自动注入 AI 聊天组件到部署目录
# 功能：将 index.html 中的 AI 聊天组件注入到 .deploy_git/index.html
# 作者：AI Assistant
# 日期：2026-03-19
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
SOURCE_FILE="index.html"
DEPLOY_FILE=".deploy_git/index.html"
BACKUP_DIR=".backups"

echo -e "${PURPLE}========================================${NC}"
echo -e "${PURPLE}  AI 聊天组件自动注入工具${NC}"
echo -e "${PURPLE}========================================${NC}"
echo ""

# 检查文件是否存在
if [ ! -f "$SOURCE_FILE" ]; then
    echo -e "${RED}❌ 错误：源文件不存在：$SOURCE_FILE${NC}"
    exit 1
fi

if [ ! -f "$DEPLOY_FILE" ]; then
    echo -e "${RED}❌ 错误：部署文件不存在：$DEPLOY_FILE${NC}"
    echo -e "${YELLOW}💡 提示：请先运行 hexo generate 和 hexo deploy${NC}"
    exit 1
fi

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份部署文件
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/index.html.$TIMESTAMP.bak"
cp "$DEPLOY_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✓ 已创建备份：$BACKUP_FILE${NC}"
echo ""

# 提取 AI 聊天组件代码
echo -e "${BLUE}📋 提取 AI 聊天组件...${NC}"

# 查找 <!-- AI 悬浮聊天按钮 --> 到 </body> 之前的内容
AI_CHAT_SECTION=$(awk '/<!-- AI 悬浮聊天按钮 -->/{flag=1} flag && /<\/body>/{exit} flag' "$SOURCE_FILE")

if [ -z "$AI_CHAT_SECTION" ]; then
    echo -e "${RED}❌ 错误：源文件中未找到 AI 聊天组件${NC}"
    echo -e "${YELLOW}💡 提示：确保源文件包含 <!-- AI 悬浮聊天按钮 --> 注释${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 成功提取 AI 聊天组件${NC}"
echo ""

# 检查部署文件是否已包含 AI 聊天组件
if grep -q "aiFloatBtn" "$DEPLOY_FILE"; then
    echo -e "${YELLOW}⚠️  警告：部署文件已包含 AI 聊天组件${NC}"
    echo -e "${YELLOW}   是否要覆盖？(y/n)${NC}"
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}操作已取消${NC}"
        exit 0
    fi
fi

# 注入到 </body> 标签之前
echo -e "${BLUE}🔧 正在注入 AI 聊天组件...${NC}"

# 使用 sed 在 </body> 前插入
sed -i.bak "/<\/body>/i\\
$AI_CHAT_SECTION
" "$DEPLOY_FILE"

# 清理备份
rm -f "${DEPLOY_FILE}.bak"

echo -e "${GREEN}✓ AI 聊天组件已成功注入${NC}"
echo ""

# 验证注入结果
if grep -q "aiFloatBtn" "$DEPLOY_FILE"; then
    echo -e "${GREEN}✅ 验证通过：AI 聊天组件已正确注入${NC}"
    echo ""
    
    # 显示统计信息
    ORIGIN_SIZE=$(wc -c < "$BACKUP_FILE")
    NEW_SIZE=$(wc -c < "$DEPLOY_FILE")
    ADDED_SIZE=$((NEW_SIZE - ORIGIN_SIZE))
    
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}  注入完成统计${NC}"
    echo -e "${PURPLE}========================================${NC}"
    echo -e "原始大小：${CYAN}$ORIGIN_SIZE bytes${NC}"
    echo -e "新大小：${GREEN}$NEW_SIZE bytes${NC}"
    echo -e "增加：${GREEN}+$ADDED_SIZE bytes${NC}"
    echo ""
    
    echo -e "${CYAN}💡 下一步操作:${NC}"
    echo "   cd .deploy_git && git add index.html && git commit && git push origin main:gh-pages"
    echo ""
    
    echo -e "${GREEN}🎉 所有操作完成!${NC}"
else
    echo -e "${RED}❌ 错误：注入失败，AI 聊天组件未找到${NC}"
    echo -e "${YELLOW}💡 正在恢复备份...${NC}"
    cp "$BACKUP_FILE" "$DEPLOY_FILE"
    echo -e "${YELLOW}✓ 已恢复到原始状态${NC}"
    exit 1
fi
