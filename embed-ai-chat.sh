#!/bin/bash
# ============================================================================
# AI 聊天助手自动嵌入工具
# 功能：为 Hexo 博客文章页面自动嵌入 AI 聊天助手组件
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

# 配置参数
CONFIG_FILE=".env"
POSTS_DIR="source/_posts"
CHAT_COMPONENT="/ai-chat.html"
EMBED_MODE="button"  # button, embed, sidebar

# AI 聊天组件 HTML 代码
AI_CHAT_COMPONENT='
<!-- AI 聊天助手嵌入 -->
<div style="margin-top: 60px; padding: 30px 0; border-top: 2px dashed #ddd;">
  <h3 style="text-align: center; margin-bottom: 20px; color: #667eea;">
    🤖 需要专业咨询？AI 助手随时为您服务！
  </h3>
  <p style="text-align: center; color: #666; margin-bottom: 30px;">
    如果您有任何问题，欢迎使用我们的 AI 智能助手获取即时帮助。
  </p>
  <div style="text-align: center;">
    <button onclick="document.getElementById('\''article-ai-iframe'\'').style.display='\''block'\''; this.style.display='\''none'\'';" 
            style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 15px 40px; border-radius: 25px; font-size: 16px; cursor: pointer; box-shadow: 0 4px 15px rgba(102,126,234,0.4); transition: all 0.3s ease;">
      💬 打开 AI 聊天助手
    </button>
  </div>
  <iframe id="article-ai-iframe" src="'"$CHAT_COMPONENT"'" 
          style="display: none; width: 100%; height: 600px; border: none; border-radius: 12px; margin-top: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.15);" 
          title="AI 智能聊天助手" loading="lazy">
  </iframe>
  <script>
    // 支持 ESC 键关闭 iframe
    document.addEventListener('\''keydown'\'', function(e) {
      if (e.key === '\''Escape'\'') {
        document.getElementById('\''article-ai-iframe'\'').style.display = '\''none'\'';
        const btn = document.querySelector('\''button[onclick*="article-ai-iframe"]'\'');
        if (btn) btn.style.display = '\''inline-block'\'';
      }
    });
  </script>
</div>'

# 显示使用说明
show_usage() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}  AI 聊天助手自动嵌入工具${NC}"
    echo -e "${PURPLE}========================================${NC}"
    echo ""
    echo -e "${CYAN}用法:${NC}"
    echo "  $0 [选项]"
    echo ""
    echo -e "${CYAN}选项:${NC}"
    echo "  --all           为所有文章添加 AI 聊天组件"
    echo "  --latest        仅为最新文章添加"
    echo "  --file=FILE     为指定文件添加"
    echo "  --remove        移除所有文章的 AI 聊天组件"
    echo "  --check         检查已嵌入的文章"
    echo "  --help          显示此帮助信息"
    echo ""
    echo -e "${CYAN}示例:${NC}"
    echo "  $0 --all                    # 处理所有文章"
    echo "  $0 --latest                 # 处理最新文章"
    echo "  $0 --file=my-post.md        # 处理指定文章"
    echo "  $0 --remove                 # 移除所有嵌入"
    echo ""
}

# 检查文件是否存在
check_files() {
    if [ ! -d "$POSTS_DIR" ]; then
        echo -e "${RED}❌ 错误：文章目录不存在：$POSTS_DIR${NC}"
        exit 1
    fi
    
    if [ ! -f "$CHAT_COMPONENT" ] && [ "$CHAT_COMPONENT" != "/ai-chat.html" ]; then
        echo -e "${YELLOW}⚠️  警告：AI 聊天组件文件不存在：$CHAT_COMPONENT${NC}"
        echo -e "${YELLOW}   将使用默认的 /ai-chat.html 路径${NC}"
    fi
}

# 为单篇文章添加 AI 聊天组件
add_chat_component() {
    local file=$1
    local filename=$(basename "$file")
    
    if grep -q "article-ai-iframe" "$file"; then
        echo -e "${YELLOW}⚠️  跳过：$filename 已包含 AI 聊天组件${NC}"
        return 0
    fi
    
    # 在文章末尾添加 AI 聊天组件
    # 找到 </script> 标签（front-matter 结束位置）
    if grep -q "</script>" "$file"; then
        # 在最后一个 </script> 后添加
        awk '
        BEGIN { found = 0 }
        /<\/script>/ { 
            print; 
            if (found == 0) {
                found = 1;
                system("cat << '\''EOF'\''");
            }
            next;
        }
        { print }
        ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
        
        # 追加内容
        echo "$AI_CHAT_COMPONENT" >> "$file"
        
        echo -e "${GREEN}✓ 已添加：$filename${NC}"
    else
        echo -e "${RED}❌ 错误：$filename 格式异常，缺少 </script> 标签${NC}"
        return 1
    fi
}

# 移除 AI 聊天组件
remove_chat_component() {
    local file=$1
    local filename=$(basename "$file")
    
    if grep -q "article-ai-iframe" "$file"; then
        # 移除 AI 聊天组件部分
        sed -i.bak '/<!-- AI 聊天助手嵌入 -->/,/<\/div>/d' "$file"
        rm -f "${file}.bak"
        echo -e "${GREEN}✓ 已移除：$filename${NC}"
    else
        echo -e "${YELLOW}⚠️  跳过：$filename 未包含 AI 聊天组件${NC}"
    fi
}

# 处理所有文章
process_all_posts() {
    echo -e "${BLUE}📊 开始处理所有文章...${NC}"
    echo ""
    
    local count=0
    local success=0
    local failed=0
    
    for file in "$POSTS_DIR"/*.md; do
        if [ -f "$file" ]; then
            ((count++))
            add_chat_component "$file"
            if [ $? -eq 0 ]; then
                ((success++))
            else
                ((failed++))
            fi
        fi
    done
    
    echo ""
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}  处理完成!${NC}"
    echo -e "${PURPLE}========================================${NC}"
    echo -e "总文章数：${CYAN}$count${NC}"
    echo -e "成功：${GREEN}$success${NC}"
    echo -e "失败：${RED}$failed${NC}"
    echo ""
}

# 处理最新文章
process_latest_post() {
    echo -e "${BLUE}📰 处理最新文章...${NC}"
    echo ""
    
    local latest=$(ls -t "$POSTS_DIR"/*.md 2>/dev/null | head -1)
    
    if [ -n "$latest" ] && [ -f "$latest" ]; then
        add_chat_component "$latest"
        echo ""
        echo -e "${GREEN}✓ 最新文章已更新：$(basename "$latest")${NC}"
    else
        echo -e "${RED}❌ 错误：未找到文章${NC}"
        exit 1
    fi
}

# 检查已嵌入的文章
check_embedded() {
    echo -e "${BLUE}🔍 检查已嵌入 AI 聊天组件的文章...${NC}"
    echo ""
    
    local count=0
    
    for file in "$POSTS_DIR"/*.md; do
        if [ -f "$file" ] && grep -q "article-ai-iframe" "$file"; then
            echo -e "${GREEN}✓ $(basename "$file")${NC}"
            ((count++))
        fi
    done
    
    echo ""
    echo -e "${PURPLE}共 ${CYAN}$count${PURPLE} 篇文章已嵌入 AI 聊天助手${NC}"
    echo ""
}

# 移除所有文章的 AI 聊天组件
remove_all() {
    echo -e "${YELLOW}⚠️  警告：此操作将移除所有文章的 AI 聊天组件${NC}"
    echo -e "${YELLOW}   确定要继续吗？(y/n)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🗑️  开始移除...${NC}"
        echo ""
        
        for file in "$POSTS_DIR"/*.md; do
            if [ -f "$file" ]; then
                remove_chat_component "$file"
            fi
        done
        
        echo ""
        echo -e "${GREEN}✓ 所有文章的 AI 聊天组件已移除${NC}"
    else
        echo -e "${YELLOW}操作已取消${NC}"
    fi
}

# 主函数
main() {
    echo ""
    
    # 解析命令行参数
    case "${1:-}" in
        --all)
            check_files
            process_all_posts
            ;;
        --latest)
            check_files
            process_latest_post
            ;;
        --file=*)
            check_files
            file="${1#--file=}"
            if [ -f "$file" ]; then
                add_chat_component "$file"
            else
                echo -e "${RED}❌ 错误：文件不存在：$file${NC}"
                exit 1
            fi
            ;;
        --remove)
            remove_all
            ;;
        --check)
            check_embedded
            ;;
        --help|-h|"")
            show_usage
            ;;
        *)
            echo -e "${RED}❌ 未知选项：$1${NC}"
            show_usage
            exit 1
            ;;
    esac
    
    # 提示是否需要生成和部署
    if [ "${1:-}" != "--help" ] && [ "${1:-}" != "-h" ] && [ "${1:-}" != "" ]; then
        echo -e "${CYAN}💡 提示：运行以下命令使更改生效:${NC}"
        echo "   hexo clean && hexo generate && hexo deploy"
        echo ""
    fi
}

# 执行主函数
main "$@"
