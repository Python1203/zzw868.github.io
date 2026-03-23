#!/bin/bash
# 自动合并所有 HTML 组件到 index.html 的增强版本
# 此脚本会创建一个包含所有组件功能的综合演示页面

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  HTML 组件自动整合工具${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 检查文件是否存在
check_files() {
    local files=(
        "test-stock-chart.html"
        "crypto-dashboard.html"
        "contact-form.html"
        "navbar.html"
        "grid-layout.html"
        "3-column-layout.html"
        "modal-popup.html"
        "fade-in-animation.html"
        "modern-button.html"
        "tailwind-card-component.html"
        "react-counter-demo.html"
        "components-hub.html"
    )
    
    echo -e "${BLUE}检查组件文件...${NC}"
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✓ ${file}${NC}"
        else
            echo -e "${RED}✗ ${file} (未找到)${NC}"
        fi
    done
    echo ""
}

# 创建综合演示页面的头部
create_demo_header() {
    cat << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全组件演示 - 张良信息咨询服务工作室</title>
    <style>
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-gradient);
            min-height: 100vh;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 50px;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 20px;
            text-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.3rem;
            opacity: 0.95;
        }
        
        .iframe-container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .component-frame {
            width: 100%;
            height: 800px;
            border: none;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 2rem;
            color: var(--primary-color);
            margin: 40px 0 20px 0;
            padding-bottom: 15px;
            border-bottom: 3px solid var(--primary-color);
        }
        
        .back-link {
            display: inline-block;
            margin-top: 30px;
            padding: 15px 40px;
            background: white;
            color: var(--primary-color);
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .back-link:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 全组件演示中心</h1>
            <p>一站式查看所有 HTML 组件效果</p>
        </div>
        
        <div class="iframe-container">
EOF
}

# 创建综合演示页面的尾部
create_demo_footer() {
    cat << 'EOF'
            <div style="text-align: center;">
                <a href="/index.html" class="back-link">← 返回主页</a>
                <a href="/components-hub.html" class="back-link" style="margin-left: 20px;">浏览组件导航 →</a>
            </div>
        </div>
    </div>
</body>
</html>
EOF
}

# 生成综合演示页面
generate_demo_page() {
    echo -e "${BLUE}正在生成综合演示页面...${NC}"
    
    local output_file="all-components-demo.html"
    
    # 创建文件头部
    create_demo_header > "$output_file"
    
    # 添加组件列表
    local components=(
        "test-stock-chart.html:实时股票价格预测"
        "crypto-dashboard.html:加密货币仪表板"
        "contact-form.html:联系表单"
        "navbar.html:响应式导航栏"
        "grid-layout.html:CSS Grid 布局"
        "3-column-layout.html:三栏布局"
        "modal-popup.html:模态弹窗"
        "fade-in-animation.html:淡入动画"
        "modern-button.html:现代按钮"
        "tailwind-card-component.html:Tailwind 卡片"
        "react-counter-demo.html:React 计数器"
    )
    
    for component in "${components[@]}"; do
        IFS=':' read -r file title <<< "$component"
        if [ -f "$file" ]; then
            echo -e "${GREEN}  ✓ 添加：$title${NC}"
            cat >> "$output_file" << EOF

            <h2 class="section-title">📌 $title</h2>
            <iframe src="$file" class="component-frame" title="$title"></iframe>
EOF
        fi
    done
    
    # 添加文件尾部
    create_demo_footer >> "$output_file"
    
    echo -e "${GREEN}✓ 综合演示页面生成完成：${CYAN}$output_file${NC}"
    echo ""
}

# 更新索引链接
update_index_links() {
    echo -e "${BLUE}检查 index.html 中的组件链接...${NC}"
    
    if grep -q "components-hub.html" index.html; then
        echo -e "${GREEN}✓ 组件导航链接已存在${NC}"
    else
        echo -e "${YELLOW}⚠ 建议手动添加 components-hub.html 链接到 index.html${NC}"
    fi
    echo ""
}

# 显示使用说明
show_usage() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}  使用指南${NC}"
    echo -e "${PURPLE}========================================${NC}"
    echo ""
    echo -e "${CYAN}生成的文件:${NC}"
    echo "  - components-hub.html (组件导航中心)"
    echo "  - all-components-demo.html (综合演示页面)"
    echo ""
    echo -e "${CYAN}访问方式:${NC}"
    echo "  1. 在浏览器中打开 components-hub.html 查看组件导航"
    echo "  2. 在浏览器中打开 all-components-demo.html 查看所有组件演示"
    echo "  3. 通过 index.html 首页的特色功能区域访问各个组件"
    echo ""
    echo -e "${CYAN}下一步操作:${NC}"
    echo "  运行 ./auto-deploy.sh 部署到 GitHub Pages"
    echo ""
}

# 主函数
main() {
    echo -e "${YELLOW}开始整合 HTML 组件...${NC}"
    echo ""
    
    check_files
    generate_demo_page
    update_index_links
    show_usage
    
    echo -e "${GREEN}✅ 所有操作完成!${NC}"
    echo ""
}

# 执行主函数
main
