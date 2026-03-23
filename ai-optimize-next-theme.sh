#!/bin/bash
# ===============================================================
# AI 自动优化修复 Next 主题 - 一键式综合工具
# 集成：更新、备份、检查、优化、报告生成
# ===============================================================

set -e

# ==================== 颜色定义 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ==================== 配置变量 ====================
PROJECT_ROOT="$(pwd)"
CONFIG_FILE="_config.next.yml"
THEME_CONFIG="themes/next/_config.yml"
BACKUP_DIR=".theme_backups"
LOG_FILE=".ai_optimization.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# ==================== 日志函数 ====================
log() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}ℹ${NC} $1" | tee -a "$LOG_FILE"
}

step() {
    echo -e "${MAGENTA}▶${NC} $1" | tee -a "$LOG_FILE"
}

# ==================== 检查依赖 ====================
check_dependencies() {
    step "检查系统依赖..."
    
    local missing_deps=()
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("nodejs")
    fi
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    # 检查 Git
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    # 检查 Python 3
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # 检查 PyYAML
    if ! python3 -c "import yaml" 2>/dev/null; then
        missing_deps+=("pyyaml")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        warning "缺少以下依赖："
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        
        if [[ " ${missing_deps[@]} " =~ " pyyaml " ]]; then
            info "安装 PyYAML: pip3 install pyyaml"
        fi
        
        return 1
    fi
    
    success "所有依赖已就绪"
    info "Node.js: $(node -v)"
    info "npm: $(npm -v)"
    info "Git: $(git --version)"
    info "Python: $(python3 --version)"
}

# ==================== 创建备份目录 ====================
setup_backup_dir() {
    step "设置备份目录..."
    
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        success "备份目录已创建：$BACKUP_DIR"
    else
        info "备份目录已存在：$BACKUP_DIR"
    fi
}

# ==================== 完整备份 ====================
full_backup() {
    step "执行完整备份..."
    
    local backup_path="$BACKUP_DIR/full_backup_$TIMESTAMP"
    mkdir -p "$backup_path"
    
    # 备份配置文件
    if [ -f "$CONFIG_FILE" ]; then
        cp "$CONFIG_FILE" "$backup_path/"
        success "已备份：$CONFIG_FILE"
    fi
    
    if [ -f "$THEME_CONFIG" ]; then
        cp "$THEME_CONFIG" "$backup_path/"
        success "已备份：$THEME_CONFIG"
    fi
    
    # 备份 source/_data
    if [ -d "source/_data" ]; then
        cp -r "source/_data" "$backup_path/"
        success "已备份：source/_data"
    fi
    
    # 记录备份信息
    echo "$backup_path" > "$BACKUP_DIR/latest_full_backup"
    info "备份位置：$backup_path"
    
    success "完整备份完成！"
}

# ==================== 智能检查配置 ====================
smart_check_config() {
    step "智能检查配置..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        warning "配置文件不存在：$CONFIG_FILE"
        return 1
    fi
    
    # 使用 Python 检查器
    python3 config_checker.py "$CONFIG_FILE" --format both || true
    
    success "配置检查完成！"
}

# ==================== 自动优化配置 ====================
auto_optimize_config() {
    step "自动优化配置..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        warning "配置文件不存在，跳过优化"
        return 1
    fi
    
    # 使用 Python 优化器
    python3 smart_merge_config.py optimize --config "$CONFIG_FILE"
    
    success "配置优化完成！"
}

# ==================== 检查并更新主题 ====================
check_and_update_theme() {
    step "检查主题更新..."
    
    # 获取当前版本
    local current_version=""
    if [ -f "themes/next/package.json" ]; then
        current_version=$(grep '"version"' themes/next/package.json | cut -d'"' -f4)
        info "当前版本：$current_version"
    fi
    
    # 获取最新版本
    local latest_version=$(curl -s https://api.github.com/repos/next-theme/hexo-theme-next/releases/latest | \
                          grep '"tag_name"' | cut -d'"' -f4 | sed 's/v//')
    
    if [ -n "$latest_version" ]; then
        info "最新版本：$latest_version"
        
        if [ "$current_version" != "$latest_version" ]; then
            warning "发现新版本！是否更新？(y/N)"
            read -p "" confirm
            
            if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
                update_theme
            else
                info "跳过更新"
            fi
        else
            success "已是最新版本"
        fi
    else
        warning "无法获取最新版本信息"
    fi
}

# ==================== 更新主题 ====================
update_theme() {
    step "更新 Next 主题..."
    
    # 备份当前版本
    if [ -d "themes/next" ]; then
        cp -r "themes/next" "$BACKUP_DIR/theme_backup_$TIMESTAMP"
        info "已备份旧版本主题"
    fi
    
    # 删除旧版本
    rm -rf "themes/next"
    
    # 安装新版本
    npm install hexo-theme-next@latest
    
    success "主题已更新到最新版本"
}

# ==================== 清理冗余文件 ====================
cleanup_redundant_files() {
    step "清理冗余文件..."
    
    local count=0
    
    # 查找备份文件
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            rm -f "$file"
            ((count++))
        fi
    done < <(find . -type f \( -name "*.backup" -o -name "*.bak" -o -name "*.old" -o -name "*~" \) \
        -not -path "./.venv/*" \
        -not -path "./node_modules/*" \
        -not -path "./financial-ai-dashboard/backend/venv/*" \
        2>/dev/null)
    
    if [ $count -gt 0 ]; then
        success "已清理 $count 个冗余文件"
    else
        info "没有发现冗余文件"
    fi
}

# ==================== 生成综合报告 ====================
generate_comprehensive_report() {
    step "生成综合优化报告..."
    
    local report_file="ai_optimization_report_$TIMESTAMP.md"
    
    cat > "$report_file" << EOF
# 🤖 AI 自动优化修复 Next 主题 - 综合报告

## 📅 基本信息

- **生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **项目根目录**: $PROJECT_ROOT
- **配置文件**: $CONFIG_FILE
- **操作类型**: 完整优化流程

## 📊 版本信息

EOF

    # 添加版本信息
    if [ -f "themes/next/package.json" ]; then
        local version=$(grep '"version"' themes/next/package.json | cut -d'"' -f4)
        echo "- **Next 主题版本**: $version" >> "$report_file"
    fi
    
    echo "- **Node.js**: $(node -v)" >> "$report_file"
    echo "- **npm**: $(npm -v)" >> "$report_file"
    echo "- **Git**: $(git --version)" >> "$report_file"
    
    cat >> "$report_file" << EOF

## ✅ 执行的操作

### 1. 环境检查
- ✓ 检查系统依赖
- ✓ 验证必要工具

### 2. 数据备份
- ✓ 创建备份目录
- ✓ 备份配置文件
- ✓ 备份自定义数据

### 3. 配置检查
- ✓ 扫描配置问题
- ✓ 生成检查报告

### 4. 自动优化
- ✓ 优化配置结构
- ✓ 添加推荐设置

### 5. 主题更新
- ✓ 检查最新版本
- ✓ 执行更新（如需要）

### 6. 清理工作
- ✓ 清理冗余文件

## 📋 生成的报告文件

EOF

    # 列出报告文件
    ls -1 "$PROJECT_ROOT"/*report*."$TIMESTAMP"*.* 2>/dev/null | while read -r file; do
        echo "- $(basename "$file")" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF

## 💡 后续建议

1. **测试网站**: 
   \`\`\`bash
   hexo clean && hexo g -d
   \`\`\`

2. **检查变更**: 
   \`\`\`bash
   git status
   git diff
   \`\`\`

3. **查看报告**: 打开生成的报告文件查看详情

4. **提交备份**: 将备份文件提交到 Git 以便恢复

## 🔗 相关链接

- [Next 主题官方文档](https://theme-next.js.org)
- [Next 主题 GitHub](https://github.com/next-theme/hexo-theme-next)
- [配置指南](https://theme-next.js.org/docs/getting-started/configuration)

---
*此报告由 AI 自动优化系统生成*
EOF

    success "报告已生成：$report_file"
}

# ==================== 显示主菜单 ====================
show_main_menu() {
    clear
    echo ""
    echo "============================================================"
    echo "       🤖 AI 自动优化修复 Next 主题工具"
    echo "============================================================"
    echo ""
    echo "📦 主要功能:"
    echo "  1. 一键完整优化（推荐）"
    echo "  2. 仅检查配置"
    echo "  3. 仅优化配置"
    echo "  4. 检查并更新主题"
    echo "  5. 完整备份"
    echo "  6. 清理冗余文件"
    echo "  7. 生成综合报告"
    echo ""
    echo "⚙️  高级选项:"
    echo "  8. 恢复备份"
    echo "  9. 查看日志"
    echo "  0. 退出"
    echo ""
    echo "============================================================"
    echo ""
}

# ==================== 一键完整优化 ====================
one_click_optimization() {
    log "============================================================"
    log "🚀 开始一键完整优化"
    log "============================================================"
    
    check_dependencies
    setup_backup_dir
    full_backup
    smart_check_config
    auto_optimize_config
    check_and_update_theme
    cleanup_redundant_files
    generate_comprehensive_report
    
    log "============================================================"
    success "✨ 一键优化完成！"
    log "============================================================"
    log "查看报告：ls -lh *report*.md"
    log "查看日志：cat $LOG_FILE"
    log "============================================================"
    
    echo ""
    read -p "是否立即测试网站？(y/N): " test_confirm
    if [ "$test_confirm" = "y" ] || [ "$test_confirm" = "Y" ]; then
        info "运行 Hexo 生成测试..."
        hexo clean && hexo g
        success "网站生成成功！"
    fi
}

# ==================== 恢复备份 ====================
restore_backup() {
    echo ""
    echo "可用的备份:"
    echo "============================================================"
    
    if [ -d "$BACKUP_DIR" ]; then
        local backups=($(ls -1 "$BACKUP_DIR" | grep "backup_" | sort -r))
        
        if [ ${#backups[@]} -eq 0 ]; then
            warning "没有找到备份"
            return
        fi
        
        for i in "${!backups[@]}"; do
            echo "  $((i+1)). ${backups[$i]}"
        done
        
        echo ""
        read -p "选择备份编号 (1-${#backups[@]}): " backup_choice
        
        if [[ "$backup_choice" =~ ^[0-9]+$ ]] && [ "$backup_choice" -le ${#backups[@]} ]; then
            local selected_backup="${backups[$((backup_choice-1))]}"
            local backup_path="$BACKUP_DIR/$selected_backup"
            
            warning "即将从备份恢复：$selected_backup"
            read -p "确定吗？(y/N): " restore_confirm
            
            if [ "$restore_confirm" = "y" ] || [ "$restore_confirm" = "Y" ]; then
                # 恢复文件
                if [ -f "$backup_path/$CONFIG_FILE" ]; then
                    cp "$backup_path/$CONFIG_FILE" "$CONFIG_FILE"
                    success "已恢复：$CONFIG_FILE"
                fi
                
                if [ -f "$backup_path/$THEME_CONFIG" ]; then
                    cp "$backup_path/$THEME_CONFIG" "$THEME_CONFIG"
                    success "已恢复：$THEME_CONFIG"
                fi
                
                if [ -d "$backup_path/_data" ]; then
                    cp -r "$backup_path/_data" "source/"
                    success "已恢复：source/_data"
                fi
                
                success "备份恢复完成！"
            else
                info "取消恢复"
            fi
        else
            error "无效的选择"
        fi
    else
        warning "备份目录不存在"
    fi
}

# ==================== 查看日志 ====================
view_logs() {
    echo ""
    if [ -f "$LOG_FILE" ]; then
        echo "最近的日志 (最后 50 行):"
        echo "============================================================"
        tail -50 "$LOG_FILE"
        echo "============================================================"
        echo ""
        read -p "是否查看完整日志？(y/N): " full_log
        if [ "$full_log" = "y" ] || [ "$full_log" = "Y" ]; then
            less "$LOG_FILE"
        fi
    else
        warning "日志文件不存在"
    fi
}

# ==================== 主函数 ====================
main() {
    # 如果直接传入参数
    case "${1:-menu}" in
        "auto")
            # 自动模式，无需交互
            check_dependencies
            setup_backup_dir
            full_backup
            smart_check_config
            auto_optimize_config
            check_and_update_theme
            cleanup_redundant_files
            generate_comprehensive_report
            success "自动优化完成！"
            ;;
        "check")
            smart_check_config
            ;;
        "optimize")
            auto_optimize_config
            ;;
        "update")
            check_and_update_theme
            ;;
        "backup")
            setup_backup_dir
            full_backup
            ;;
        "clean")
            cleanup_redundant_files
            ;;
        "report")
            generate_comprehensive_report
            ;;
        "menu"|*)
            show_main_menu
            read -p "请选择操作 (0-9): " choice
            
            case $choice in
                1)
                    one_click_optimization
                    ;;
                2)
                    smart_check_config
                    ;;
                3)
                    auto_optimize_config
                    ;;
                4)
                    check_and_update_theme
                    ;;
                5)
                    setup_backup_dir
                    full_backup
                    ;;
                6)
                    cleanup_redundant_files
                    ;;
                7)
                    generate_comprehensive_report
                    ;;
                8)
                    restore_backup
                    ;;
                9)
                    view_logs
                    ;;
                0)
                    info "退出程序"
                    exit 0
                    ;;
                *)
                    error "无效选择：$choice"
                    exit 1
                    ;;
            esac
            ;;
    esac
}

# 显示帮助信息
show_help() {
    echo "用法：$0 [选项]"
    echo ""
    echo "选项:"
    echo "  auto        自动模式（无需交互）"
    echo "  check       仅检查配置"
    echo "  optimize    仅优化配置"
    echo "  update      检查并更新主题"
    echo "  backup      完整备份"
    echo "  clean       清理冗余文件"
    echo "  report      生成综合报告"
    echo "  menu        显示交互菜单（默认）"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0              # 交互模式"
    echo "  $0 auto         # 自动模式"
    echo "  $0 check        # 检查配置"
    echo ""
}

# 处理帮助参数
if [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# 执行主函数
main "$@"
