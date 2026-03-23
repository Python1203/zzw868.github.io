#!/bin/bash
# HTML 文件合并工具 - 快速启动脚本

echo "🚀 HTML 文件合并工具"
echo "===================="
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python 3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"
echo ""

# 检查依赖
echo "📦 检查依赖..."
if ! python3 -c "import bs4" 2>/dev/null; then
    echo "⚠️  未找到 beautifulsoup4，正在安装..."
    pip3 install beautifulsoup4
else
    echo "✅ beautifulsoup4 已安装"
fi
echo ""

# 创建示例目录（如果不存在）
if [ ! -d "my_pages" ]; then
    echo "📁 创建示例目录 my_pages/ ..."
    mkdir -p my_pages
    
    # 创建示例 HTML 文件
    cat > my_pages/page1.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>页面 1</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>这是页面 1</h1>
    <p>这是第一个示例页面的内容。</p>
</body>
</html>
EOF
    
    cat > my_pages/page2.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>页面 2</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>这是页面 2</h1>
    <p>这是第二个示例页面的内容。</p>
</body>
</html>
EOF
    
    cat > my_pages/page3.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>页面 3</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>这是页面 3</h1>
    <p>这是第三个示例页面的内容。</p>
</body>
</html>
EOF
    
    echo "✅ 已创建 3 个示例 HTML 文件"
    echo ""
fi

# 运行合并脚本
echo "🔄 开始合并 HTML 文件..."
echo ""
python3 merge_html.py

# 检查结果
if [ $? -eq 0 ] && [ -f "merged.html" ]; then
    echo ""
    echo "✨ 合并成功！"
    echo "📄 输出文件：merged.html"
    echo ""
    
    # 询问是否用浏览器打开
    if command -v open &> /dev/null; then
        read -p "是否现在用浏览器打开？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open merged.html
        fi
    fi
else
    echo ""
    echo "❌ 合并失败，请检查错误信息"
    exit 1
fi
