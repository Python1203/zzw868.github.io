#!/bin/bash
# Pandoc HTML 合并工具 - 快速脚本

echo "🚀 Pandoc HTML 合并工具"
echo "======================"
echo ""

# 检查 Pandoc 是否安装
if ! command -v pandoc &> /dev/null; then
    echo "❌ 未找到 Pandoc，正在检查安装方式..."
    echo ""
    
    # macOS
    if command -v brew &> /dev/null; then
        echo "🍺 检测到 Homebrew，正在安装 Pandoc..."
        brew install pandoc
    # Linux
    elif command -v apt-get &> /dev/null; then
        echo "🐧 检测到 APT，正在安装 Pandoc..."
        sudo apt-get update && sudo apt-get install pandoc
    else
        echo "⚠️  请手动安装 Pandoc:"
        echo "   - macOS: brew install pandoc"
        echo "   - Linux: sudo apt-get install pandoc"
        echo "   - Windows: https://pandoc.org/installing.html"
        exit 1
    fi
fi

echo "✅ Pandoc 版本信息:"
pandoc --version | head -1
echo ""

# 检查是否有 HTML 文件
if [ ! -d "my_pages" ]; then
    echo "❌ 目录 my_pages/ 不存在"
    echo "请先将要合并的 HTML 文件放到 my_pages/ 目录中"
    exit 1
fi

HTML_FILES=$(find my_pages -name "*.html" | wc -l)
if [ "$HTML_FILES" -eq 0 ]; then
    echo "❌ my_pages/ 中没有找到 HTML 文件"
    exit 1
fi

echo "📁 找到 $HTML_FILES 个 HTML 文件"
echo ""

# 获取所有 HTML 文件列表
FILES=""
for file in my_pages/*.html; do
    if [ -f "$file" ]; then
        FILES="$FILES $file"
        echo "   - $(basename $file)"
    fi
done
echo ""

# 执行 Pandoc 合并
echo "🔧 正在使用 Pandoc 合并..."
echo ""

# 基础合并（最简单）
pandoc $FILES -s -o merged_pandoc.html

if [ $? -eq 0 ]; then
    echo "✅ Pandoc 合并成功！"
    echo "📄 输出文件：merged_pandoc.html"
    echo "📊 文件大小：$(du -h merged_pandoc.html | cut -f1)"
    echo ""
    
    # 询问是否打开
    if command -v open &> /dev/null; then
        read -p "是否现在用浏览器打开？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open merged_pandoc.html
        fi
    fi
else
    echo "❌ Pandoc 合并失败"
    exit 1
fi
