#!/bin/bash
# 博客优化修复脚本 - 一键修复所有常见问题
set -e

echo "============================================================"
echo "🔧 博客优化修复工具"
echo "============================================================"
echo "时间：$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查 Node.js 和 npm
echo "📦 Step 1: 检查环境..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    exit 1
fi
echo "✓ Node.js: $(node --version)"
echo "✓ npm: $(npm --version)"
echo ""

# 2. 检查并修复 package.json
echo "📝 Step 2: 检查依赖配置..."
if grep -q '"hexo-pwa": "\^1.1.0"' package.json; then
    echo -e "${YELLOW}⚠️  发现 hexo-pwa 版本错误，正在修复...${NC}"
    sed -i.bak 's/"hexo-pwa": "\^1.1.0"/"hexo-pwa": "^0.1.3"/g' package.json
    rm -f package.json.bak
    echo "✓ 已修复 hexo-pwa 版本"
else
    echo "✓ package.json 配置正确"
fi
echo ""

# 3. 清理并重新安装依赖
echo "🔧 Step 3: 清理并重装依赖..."
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
echo "✓ 依赖安装完成"
echo ""

# 4. 检查 Hexo 配置
echo "⚙️  Step 4: 检查 Hexo 配置..."
if [ ! -f "_config.yml" ]; then
    echo -e "${RED}❌ _config.yml 不存在${NC}"
    exit 1
fi

# 检查是否有手动修改的 index.html（常见冲突）
if [ -f "index.html" ] && [ -f "public/index.html" ]; then
    ROOT_LINES=$(wc -l < index.html)
    PUBLIC_LINES=$(wc -l < public/index.html)
    
    if [ "$ROOT_LINES" -gt "$PUBLIC_LINES" ]; then
        echo -e "${YELLOW}⚠️  发现根目录 index.html 被手动修改（$ROOT_LINES 行），与 Hexo 生成版本（$PUBLIC_LINES 行）冲突${NC}"
        echo "正在备份并删除手动版本，让 Hexo 管理..."
        cp index.html "index.html.manual-backup-$(date +%Y%m%d_%H%M%S).bak"
        rm -f index.html
        echo "✓ 已备份冲突文件并删除"
    fi
fi

# 检查主题链接
if [ ! -L "themes/next" ]; then
    echo -e "${YELLOW}⚠️  主题链接不存在，正在创建...${NC}"
    mkdir -p themes
    ln -sf ../node_modules/hexo-theme-next themes/next
    echo "✓ 主题链接已创建"
else
    echo "✓ 主题链接正常"
fi
echo ""

# 5. 清理并生成
echo "🏗️  Step 5: 清理并生成静态文件..."
hexo clean
hexo generate

# 修复关于页面 404 问题（GitHub Pages 需要 about/index.html）
if [ -f "public/about.html" ] && [ ! -d "public/about" ]; then
    echo -e "${YELLOW}⚠️  检测到 about.html，创建 about/index.html 以兼容 GitHub Pages...${NC}"
    mkdir -p public/about
    cp public/about.html public/about/index.html
    echo "✓ 已创建 public/about/index.html"
fi

echo "✓ 生成完成"
echo ""

# 6. 检查生成的文件
echo "📄 Step 6: 检查生成结果..."
if [ ! -d "public" ]; then
    echo -e "${RED}❌ public 目录不存在${NC}"
    exit 1
fi

HTML_COUNT=$(find public -name "*.html" | wc -l | tr -d ' ')
echo "✓ 已生成 $HTML_COUNT 个 HTML 文件"

# 检查关键文件
CRITICAL_FILES=("index.html" "about.html" "cases.html")
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "public/$file" ]; then
        echo "  ✓ $file"
    else
        echo -e "${YELLOW}  ⚠️  $file 未生成${NC}"
    fi
done
echo ""

# 7. 检查最新文章
echo "📝 Step 7: 检查最新文章..."
if [ -d "source/_posts" ]; then
    LATEST_POSTS=$(ls -t source/_posts/*.md 2>/dev/null | head -3)
    if [ -n "$LATEST_POSTS" ]; then
        echo "✓ 最新文章:"
        echo "$LATEST_POSTS" | while read -r post; do
            echo "  - $(basename "$post")"
        done
    else
        echo "⚠️  暂无文章"
    fi
else
    echo -e "${YELLOW}⚠️  source/_posts 目录不存在${NC}"
fi
echo ""

# 8. Git 状态检查
echo "💾 Step 8: 检查 Git 状态..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    CHANGED=$(git status --porcelain | wc -l | tr -d ' ')
    if [ "$CHANGED" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  有 $CHANGED 个文件未提交${NC}"
        echo "提示：运行 'git add . && git commit -m \"更新\"' 提交变更"
    else
        echo "✓ Git 工作区干净"
    fi
else
    echo -e "${YELLOW}⚠️  不是 Git 仓库${NC}"
fi
echo ""

# 9. 性能优化建议
echo "🚀 Step 9: 性能优化检查..."

# 检查是否启用缓存
if grep -q "cache:" _config.next.yml; then
    echo "✓ 主题缓存已启用"
else
    echo -e "${YELLOW}⚠️  建议在 _config.next.yml 中启用缓存${NC}"
fi

# 检查 CDN 配置
if [ -f "_cdn.yml" ]; then
    echo "✓ CDN 配置文件存在"
else
    echo -e "${YELLOW}⚠️  建议配置 CDN 加速${NC}"
fi
echo ""

# 10. 输出摘要
echo "============================================================"
echo "✨ 优化修复完成！"
echo "============================================================"
echo ""
echo "📊 统计信息："
echo "   - HTML 文件：$HTML_COUNT"
echo "   - 文章数量：$(ls source/_posts/*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "   - 分类目录：$(ls -d categories/*/ 2>/dev/null | wc -l | tr -d ' ')"
echo "   - 标签目录：$(ls -d tags/*/ 2>/dev/null | wc -l | tr -d ' ')"
echo ""
echo "🌐 本地测试："
echo "   运行：hexo server"
echo "   访问：http://localhost:4000"
echo ""
echo "🚀 部署到 GitHub："
echo "   运行：hexo deploy"
echo "   或手动推送：./auto-fix-blog.sh"
echo ""
echo "💡 常见问题解决："
echo "   1. hexo-pwa 报错 → 已自动降级到 v0.1.3"
echo "   2. 主题不显示 → 检查 themes/next 链接"
echo "   3. 文章不更新 → 运行 hexo clean 清理缓存"
echo ""
echo "📅 下次自动更新：周一至周五 16:10 (北京时间)"
echo ""
