#!/bin/bash
# 本地测试 HTML 导航生成

echo "🚀 本地测试 HTML 导航生成"
echo "========================"
echo ""

# 检查 template.html 是否存在
if [ ! -f "template.html" ]; then
    echo "❌ template.html 不存在"
    echo "请先创建模板文件"
    exit 1
fi

# 检查 Python 脚本是否存在
if [ ! -f "generate_nav.py" ]; then
    echo "❌ generate_nav.py 不存在"
    exit 1
fi

# 扫描目录（默认当前目录）
SCAN_DIR="${1:-.}"

echo "📂 扫描目录：$SCAN_DIR"
echo ""

# 运行生成脚本
python3 generate_nav.py "$SCAN_DIR" template.html index.html

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 导航页面生成成功！"
    echo "📄 输出文件：index.html"
    echo ""
    
    # 询问是否用浏览器打开
    if command -v open &> /dev/null; then
        read -p "是否现在用浏览器打开预览？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open index.html
        fi
    fi
else
    echo ""
    echo "❌ 生成失败"
    exit 1
fi
