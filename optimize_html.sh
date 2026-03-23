#!/bin/bash
# AI 自动优化网页布局 - 删除冗余代码

FILE_PATH="/Users/zzw868/PycharmProjects/zzw868.github.io/2021/05/20/【财经期刊FM-Radio｜2021 年 05 月 20 日】/index.html"
BACKUP_PATH="${FILE_PATH}.backup"

echo "开始优化 HTML 文件..."
echo "文件路径：$FILE_PATH"

# 创建备份
cp "$FILE_PATH" "$BACKUP_PATH"
echo "✓ 已创建备份：$BACKUP_PATH"

# 获取原始大小
ORIGINAL_SIZE=$(wc -c < "$FILE_PATH")
echo "原始大小：$ORIGINAL_SIZE 字节"

# 1. 简化 lang 属性
sed -i '' 's/lang="zh-CN,en,default"/lang="zh-CN"/g' "$FILE_PATH"

# 2. 删除 generator meta 标签
sed -i '' '/<meta name="generator" content="Hexo/d' "$FILE_PATH"

# 3. 删除 link 标签中的 type="image/png"
sed -i '' 's/type="image\/png" //g' "$FILE_PATH"

# 4. 删除 script 标签中的 type="text/javascript"
sed -i '' 's/ type="text\/javascript"//g' "$FILE_PATH"

# 5. 压缩多个空行
sed -i '' '/^$/N;/^\n$/d' "$FILE_PATH"

# 6. 删除行尾空格
sed -i '' 's/[[:space:]]*$//' "$FILE_PATH"

# 获取优化后大小
OPTIMIZED_SIZE=$(wc -c < "$FILE_PATH")
echo "优化后大小：$OPTIMIZED_SIZE 字节"

# 计算减少的百分比
REDUCTION=$(echo "scale=2; ($ORIGINAL_SIZE - $OPTIMIZED_SIZE) * 100 / $ORIGINAL_SIZE" | bc)
echo "减少了：${REDUCTION}%"

echo "✓ 优化完成！"
echo ""
echo "如需恢复原始文件，请运行："
echo "cp $BACKUP_PATH $FILE_PATH"
