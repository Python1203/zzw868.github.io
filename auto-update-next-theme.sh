#!/bin/bash
# ===============================================================
# AI 自动优化修复更新 Next 主题
# 功能：自动检测、备份、更新、修复和优化 Next 主题配置
# ===============================================================

set -e

# ==================== 颜色定义 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ==================== 配置变量 ====================
THEME_DIR="themes/next"
BACKUP_DIR=".theme_backups"
CONFIG_FILE="_config.next.yml"
THEME_CONFIG_FILE="themes/next/_config.yml"
LOG_FILE=".ai_theme_update.log"
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

# ==================== 检查环境 ====================
check_environment() {
    log "============================================================"
    log "🤖 AI 自动优化修复更新 Next 主题"
    log "============================================================"
    
    # 检查是否在正确的目录
    if [ ! -f "package.json" ]; then
        error "请在 Hexo 博客项目根目录运行此脚本"
        exit 1
    fi
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        error "未找到 Node.js，请先安装 Node.js"
        exit 1
    fi
    
    # 检查 Git
    if ! command -v git &> /dev/null; then
        error "未找到 Git，请先安装 Git"
        exit 1
    fi
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        error "未找到 npm，请先安装 npm"
        exit 1
    fi
    
    success "环境检查通过"
    info "Node.js: $(node -v)"
    info "npm: $(npm -v)"
    info "Git: $(git --version)"
}

# ==================== 创建备份目录 ====================
create_backup_dir() {
    log "============================================================"
    log "📦 创建备份目录"
    log "============================================================"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        success "备份目录已创建：$BACKUP_DIR"
    else
        info "备份目录已存在：$BACKUP_DIR"
    fi
}

# ==================== 备份当前配置 ====================
backup_config() {
    log "============================================================"
    log "💾 备份当前配置文件"
    log "============================================================"
    
    local backup_subdir="$BACKUP_DIR/backup_$TIMESTAMP"
    mkdir -p "$backup_subdir"
    
    # 备份用户配置
    if [ -f "$CONFIG_FILE" ]; then
        cp "$CONFIG_FILE" "$backup_subdir/"
        success "已备份：$CONFIG_FILE"
    else
        warning "未找到配置文件：$CONFIG_FILE"
    fi
    
    # 备份主题配置（如果存在修改）
    if [ -f "$THEME_CONFIG_FILE" ]; then
        cp "$THEME_CONFIG_FILE" "$backup_subdir/"
        success "已备份：$THEME_CONFIG_FILE"
    fi
    
    # 备份 source/_data 目录
    if [ -d "source/_data" ]; then
        cp -r "source/_data" "$backup_subdir/"
        success "已备份：source/_data"
    fi
    
    info "备份位置：$backup_subdir"
    echo "$backup_subdir" > "$BACKUP_DIR/latest_backup"
}

# ==================== 检测当前版本 ====================
detect_current_version() {
    log "============================================================"
    log "🔍 检测当前 Next 主题版本"
    log "============================================================"
    
    if [ -f "$THEME_DIR/package.json" ]; then
        local version=$(grep '"version"' "$THEME_DIR/package.json" | cut -d'"' -f4)
        info "当前 Next 主题版本：$version"
        echo "$version"
    else
        warning "无法检测到 Next 主题版本"
        echo "unknown"
    fi
}

# ==================== 获取最新版本信息 ====================
get_latest_version_info() {
    log "============================================================"
    log "🌐 获取 Next 主题最新版本信息"
    log "============================================================"
    
    # 从 GitHub 获取最新版本
    local latest_info=$(curl -s https://api.github.com/repos/next-theme/hexo-theme-next/releases/latest)
    local latest_version=$(echo "$latest_info" | grep '"tag_name"' | cut -d'"' -f4 | sed 's/v//')
    local publish_date=$(echo "$latest_info" | grep '"published_at"' | cut -d'"' -f4 | cut -d'T' -f1)
    
    if [ -n "$latest_version" ]; then
        success "最新 Next 主题版本：$latest_version (发布日期：$publish_date)"
        info "官方文档：https://theme-next.js.org"
        echo "$latest_version"
    else
        warning "无法获取最新版本信息"
        echo ""
    fi
}

# ==================== 比较版本 ====================
compare_versions() {
    local current="$1"
    local latest="$2"
    
    if [ "$current" = "unknown" ] || [ -z "$latest" ]; then
        return 2
    fi
    
    if [ "$current" = "$latest" ]; then
        return 0
    else
        return 1
    fi
}

# ==================== 智能合并配置 ====================
smart_merge_config() {
    log "============================================================"
    log "🔧 智能合并配置文件"
    log "============================================================"
    
    local old_config="$1"
    local new_config="$2"
    local merged_config="$3"
    
    if [ ! -f "$old_config" ]; then
        warning "旧配置文件不存在：$old_config"
        return 1
    fi
    
    if [ ! -f "$new_config" ]; then
        warning "新配置文件不存在：$new_config"
        return 1
    fi
    
    # 使用 Python 脚本进行智能合并
    python3 << PYTHON_SCRIPT
import yaml
import sys

def merge_configs(old_file, new_file, output_file):
    """智能合并新旧配置文件"""
    try:
        # 读取旧配置（用户自定义）
        with open(old_file, 'r', encoding='utf-8') as f:
            old_config = yaml.safe_load(f) or {}
        
        # 读取新配置（主题默认）
        with open(new_file, 'r', encoding='utf-8') as f:
            new_config = yaml.safe_load(f) or {}
        
        # 深度合并：保留用户自定义，补充新选项
        def deep_merge(base, override):
            result = base.copy()
            for key, value in override.items():
                if key not in result:
                    result[key] = value
                elif isinstance(value, dict) and isinstance(result.get(key), dict):
                    result[key] = deep_merge(result[key], value)
            return result
        
        merged = deep_merge(old_config, new_config)
        
        # 写入合并后的配置
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(merged, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"✓ 配置合并完成：{output_file}")
        return True
    except Exception as e:
        print(f"✗ 配置合并失败：{str(e)}")
        return False

if __name__ == "__main__":
    merge_configs("$old_config", "$new_config", "$merged_config")
PYTHON_SCRIPT
}

# ==================== 更新主题 ====================
update_theme() {
    log "============================================================"
    log "📥 更新 Next 主题"
    log "============================================================"
    
    local method="$1"
    
    case $method in
        "npm")
            info "使用 npm 更新主题..."
            if [ -d "$THEME_DIR" ]; then
                # 删除旧版本
                rm -rf "$THEME_DIR"
                info "已删除旧版本主题"
            fi
            
            # 安装最新版本
            npm install hexo-theme-next@latest
            success "主题已更新到最新版本"
            ;;
            
        "git")
            info "使用 git 更新主题..."
            if [ -d "$THEME_DIR/.git" ]; then
                # 如果是 git 克隆的，直接 pull
                cd "$THEME_DIR"
                git pull origin master
                cd - > /dev/null
                success "主题已通过 git 更新"
            else
                warning "主题目录不是 git 仓库，切换到 npm 方式"
                update_theme "npm"
            fi
            ;;
            
        *)
            error "未知的更新方式：$method"
            return 1
            ;;
    esac
}

# ==================== 验证更新 ====================
verify_update() {
    log "============================================================"
    log "✅ 验证主题更新"
    log "============================================================"
    
    local new_version=$(detect_current_version)
    
    if [ "$new_version" != "unknown" ]; then
        success "主题更新成功！当前版本：$new_version"
        
        # 显示更新日志
        if [ -f "$THEME_DIR/CHANGELOG.md" ]; then
            info "查看更新日志："
            head -50 "$THEME_DIR/CHANGELOG.md"
        fi
        
        return 0
    else
        error "版本验证失败"
        return 1
    fi
}

# ==================== 清理冗余文件 ====================
cleanup_redundant_files() {
    log "============================================================"
    log "🧹 清理冗余文件"
    log "============================================================"
    
    # 查找并删除备份文件
    local backup_count=0
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            rm -f "$file"
            ((backup_count++))
        fi
    done < <(find . -type f \( -name "*.backup" -o -name "*.bak" -o -name "*.old" -o -name "*~" \) \
        -not -path "./.venv/*" \
        -not -path "./node_modules/*" \
        -not -path "./financial-ai-dashboard/backend/venv/*" \
        2>/dev/null)
    
    if [ $backup_count -gt 0 ]; then
        success "已删除 $backup_count 个备份文件"
    else
        info "没有发现冗余备份文件"
    fi
    
    # 清理 node_modules（可选）
    if [ -d "node_modules" ]; then
        local node_size=$(du -sh node_modules 2>/dev/null | cut -f1)
        info "node_modules 大小：$node_size"
        read -p "是否清理 node_modules？(y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            rm -rf node_modules
            success "已清理 node_modules"
        fi
    fi
}

# ==================== 生成报告 ====================
generate_report() {
    log "============================================================"
    log "📊 生成更新报告"
    log "============================================================"
    
    local report_file="ai_theme_update_report_$TIMESTAMP.md"
    
    cat > "$report_file" << EOF
# AI 自动优化修复更新 Next 主题 - 报告

## 📅 基本信息

- **更新时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **操作类型**: $UPDATE_TYPE
- **备份位置**: $(cat "$BACKUP_DIR/latest_backup" 2>/dev/null || echo "N/A")

## 📊 版本信息

- **更新前版本**: $CURRENT_VERSION
- **更新后版本**: $NEW_VERSION
- **最新版本**: $LATEST_VERSION

## ✅ 执行步骤

EOF

    # 添加日志到报告
    echo '```' >> "$report_file"
    tail -100 "$LOG_FILE" >> "$report_file"
    echo '```' >> "$report_file"
    
    # 添加建议
    cat >> "$report_file" << EOF

## 💡 后续建议

1. **测试网站**: 运行 \`hexo clean && hexo g -d\` 测试网站
2. **检查配置**: 对比 \`$CONFIG_FILE\` 确保配置正确
3. **查看变更**: 使用 \`git diff\` 查看文件变化
4. **提交备份**: 将备份提交到 Git 以便恢复

## 🔗 相关链接

- [Next 主题官方文档](https://theme-next.js.org)
- [Next 主题 GitHub](https://github.com/next-theme/hexo-theme-next)
- [配置指南](https://theme-next.js.org/docs/getting-started/configuration)

---
*此报告由 AI 自动优化系统生成*
EOF

    success "报告已生成：$report_file"
}

# ==================== 恢复备份 ====================
restore_backup() {
    log "============================================================"
    log "↩️  恢复备份"
    log "============================================================"
    
    local backup_path="$1"
    
    if [ -z "$backup_path" ]; then
        # 使用最新备份
        if [ -f "$BACKUP_DIR/latest_backup" ]; then
            backup_path=$(cat "$BACKUP_DIR/latest_backup")
        else
            error "未找到备份信息"
            return 1
        fi
    fi
    
    if [ ! -d "$backup_path" ]; then
        error "备份目录不存在：$backup_path"
        return 1
    fi
    
    info "从备份恢复：$backup_path"
    
    # 恢复配置文件
    if [ -f "$backup_path/$CONFIG_FILE" ]; then
        cp "$backup_path/$CONFIG_FILE" "$CONFIG_FILE"
        success "已恢复：$CONFIG_FILE"
    fi
    
    if [ -f "$backup_path/$THEME_CONFIG_FILE" ]; then
        cp "$backup_path/$THEME_CONFIG_FILE" "$THEME_CONFIG_FILE"
        success "已恢复：$THEME_CONFIG_FILE"
    fi
    
    if [ -d "$backup_path/_data" ]; then
        cp -r "$backup_path/_data" "source/"
        success "已恢复：source/_data"
    fi
    
    success "备份恢复完成！"
}

# ==================== 主函数 ====================
main() {
    local mode="${1:-interactive}"
    local update_method="${2:-npm}"
    
    # 初始化变量
    UPDATE_TYPE="full_update"
    CURRENT_VERSION=""
    NEW_VERSION=""
    LATEST_VERSION=""
    
    case $mode in
        "check")
            check_environment
            create_backup_dir
            CURRENT_VERSION=$(detect_current_version)
            LATEST_VERSION=$(get_latest_version_info)
            if compare_versions "$CURRENT_VERSION" "$LATEST_VERSION"; then
                success "已是最新版本！"
            else
                info "有新版本可用：$LATEST_VERSION"
            fi
            ;;
            
        "backup")
            check_environment
            create_backup_dir
            backup_config
            success "备份完成！"
            ;;
            
        "update")
            check_environment
            create_backup_dir
            backup_config
            
            CURRENT_VERSION=$(detect_current_version)
            LATEST_VERSION=$(get_latest_version_info)
            
            if compare_versions "$CURRENT_VERSION" "$LATEST_VERSION"; then
                warning "已是最新版本，确定要强制更新吗？(y/N): "
                read -p "" confirm
                if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
                    info "取消更新"
                    exit 0
                fi
            fi
            
            update_theme "$update_method"
            NEW_VERSION=$(detect_current_version)
            verify_update
            cleanup_redundant_files
            generate_report
            
            success "更新完成！"
            ;;
            
        "restore")
            restore_backup "$2"
            ;;
            
        "report")
            generate_report
            ;;
            
        "interactive"|*)
            check_environment
            create_backup_dir
            
            echo ""
            echo "============================================================"
            echo "请选择操作："
            echo "============================================================"
            echo "1. 检查更新（不执行更新）"
            echo "2. 备份当前配置"
            echo "3. 完整更新（备份 + 更新 + 验证）"
            echo "4. 恢复备份"
            echo "5. 生成报告"
            echo "6. 清理冗余文件"
            echo "0. 退出"
            echo "============================================================"
            echo ""
            
            read -p "请输入选项 (0-6): " choice
            
            case $choice in
                1)
                    main "check"
                    ;;
                2)
                    main "backup"
                    ;;
                3)
                    main "update" "$update_method"
                    ;;
                4)
                    echo "可用的备份:"
                    ls -1 "$BACKUP_DIR" | grep "backup_"
                    read -p "输入备份目录名称（留空使用最新）: " backup_name
                    main "restore" "$backup_name"
                    ;;
                5)
                    main "report"
                    ;;
                6)
                    cleanup_redundant_files
                    ;;
                0)
                    info "退出程序"
                    exit 0
                    ;;
                *)
                    error "无效选项：$choice"
                    exit 1
                    ;;
            esac
            ;;
    esac
    
    log "============================================================"
    log "✨ 操作完成！"
    log "============================================================"
    log "查看日志：$LOG_FILE"
}

# 显示帮助信息
show_help() {
    echo "用法：$0 [选项]"
    echo ""
    echo "选项:"
    echo "  check       检查是否有新版本"
    echo "  backup      仅备份当前配置"
    echo "  update      完整更新（备份 + 更新 + 验证）"
    echo "  restore     恢复备份"
    echo "  report      生成更新报告"
    echo "  clean       清理冗余文件"
    echo "  interactive 交互模式（默认）"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                  # 交互模式"
    echo "  $0 check            # 检查更新"
    echo "  $0 update npm       # 使用 npm 更新"
    echo "  $0 update git       # 使用 git 更新"
    echo ""
}

# 处理帮助参数
if [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# 执行主函数
main "$@"
