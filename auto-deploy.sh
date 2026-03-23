#!/bin/bash

# =====================================================
# 博客自动部署脚本
# 功能：自动推送更新到 GitHub Pages
# =====================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Git 是否安装
check_git() {
    if ! command -v git &> /dev/null; then
        log_error "Git 未安装，请先安装 Git"
        exit 1
    fi
    log_success "Git 已安装：$(git --version)"
}

# 检查 Node.js 是否安装
check_node() {
    if ! command -v node &> /dev/null; then
        log_warning "Node.js 未安装，跳过 Hexo 相关操作"
        return 1
    fi
    log_success "Node.js 已安装：$(node --version)"
    return 0
}

# 检查 Hexo 是否安装
check_hexo() {
    if ! command -v hexo &> /dev/null; then
        log_warning "Hexo 未全局安装"
        return 1
    fi
    log_success "Hexo 已安装：$(hexo --version)"
    return 0
}

# 生成静态文件
generate_site() {
    log_info "正在生成静态网站..."
    
    if check_hexo; then
        hexo clean
        hexo generate
        log_success "网站生成完成"
    else
        log_warning "Hexo 未安装，假设文件已生成"
    fi
}

# 添加 React 组件到博客
integrate_react_component() {
    log_info "正在整合 React 股票图表组件..."
    
    # 检查测试文件是否存在
    if [ -f "test-stock-chart.html" ]; then
        # 创建目标目录
        TARGET_DIR="2021/05/20/【财经期刊FM-Radio｜2021 年 05 月 20 日】"
        
        if [ -d "$TARGET_DIR" ]; then
            # 复制优化后的组件到文章目录
            cp test-stock-chart.html "$TARGET_DIR/react-component.html"
            log_success "React 组件已复制到：$TARGET_DIR/react-component.html"
        else
            log_warning "目标目录不存在：$TARGET_DIR"
        fi
        
        # 复制到 public 目录（如果存在）
        if [ -d "public" ]; then
            cp test-stock-chart.html public/
            log_success "React 组件已复制到 public/ 目录"
        fi
    else
        log_warning "test-stock-chart.html 不存在，跳过组件整合"
    fi
    
    # 运行 Node.js 注入脚本（如果存在）
    if [ -f "inject-react-component.js" ] && command -v node &> /dev/null; then
        log_info "运行 React 组件注入脚本..."
        node inject-react-component.js || log_warning "注入脚本执行失败"
    fi
}

# 添加到 Git 并提交
git_commit() {
    log_info "检查文件变更..."
    
    # 检查是否有变更
    if [ -z "$(git status --porcelain)" ]; then
        log_info "没有检测到文件变更"
        return 0
    fi
    
    # 显示变更统计
    log_info "文件变更统计："
    git status --short
    
    # 添加所有变更
    git add -A
    
    # 获取变更文件数量
    CHANGED_FILES=$(git diff --cached --name-only | wc -l)
    
    if [ $CHANGED_FILES -eq 0 ]; then
        log_info "没有需要提交的文件"
        return 0
    fi
    
    # 创建提交信息
    COMMIT_MSG="🤖 Auto Update: 更新 $CHANGED_FILES 个文件
        
- 更新时间：$(date '+%Y-%m-%d %H:%M:%S')
- 更新类型：自动部署
- 包含内容：
$(git diff --cached --name-only | sed 's/^/  - /')"

    # 提交
    git commit -m "$COMMIT_MSG"
    log_success "提交完成：$CHANGED_FILES 个文件"
}

# 推送到 GitHub
push_to_github() {
    log_info "正在推送到 GitHub..."
    
    # 检查远程仓库
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
    
    if [ -z "$REMOTE_URL" ]; then
        log_error "未配置远程仓库"
        exit 1
    fi
    
    log_info "远程仓库：$REMOTE_URL"
    
    # 推送
    git push origin main
    
    if [ $? -eq 0 ]; then
        log_success "✓ 成功推送到 GitHub Pages"
        log_info "🌐 访问地址：https://zzw868.github.io"
    else
        log_error "推送失败，请检查网络连接和权限"
        exit 1
    fi
}

# 验证部署
verify_deployment() {
    log_info "等待 GitHub Pages 部署..."
    sleep 5
    
    log_info "提示：请在浏览器中访问以下地址验证部署："
    echo "  - 主页：https://zzw868.github.io"
    echo "  - React 组件：https://zzw868.github.io/test-stock-chart.html"
    echo ""
    log_info "GitHub Actions 部署状态："
    echo "  https://github.com/zzw868/zzw868.github.io/actions"
}

# 清理临时文件
cleanup() {
    log_info "清理临时文件..."
    
    # 删除 .DS_Store 等系统文件
    find . -name ".DS_Store" -type f -delete 2>/dev/null || true
    
    log_success "清理完成"
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "   🚀 博客自动部署脚本"
    echo "   更新时间：$(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    echo ""
    
    # 进入项目目录
    cd "$(dirname "$0")"
    
    # 执行部署流程
    check_git
    integrate_react_component
    generate_site
    cleanup
    git_commit
    push_to_github
    verify_deployment
    
    echo ""
    echo "=========================================="
    echo "   ✅ 部署完成！"
    echo "=========================================="
    echo ""
}

# 捕获错误
trap 'log_error "部署过程中断"; exit 1' ERR

# 运行主函数
main "$@"
