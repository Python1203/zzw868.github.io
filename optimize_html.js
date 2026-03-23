const fs = require('fs');
const path = require('path');

// 文件路径
const filePath = '/Users/zzw868/PycharmProjects/zzw868.github.io/2021/05/20/【财经期刊FM-Radio｜2021 年 05 月 20 日】/index.html';
const backupPath = filePath + '.backup';

console.log('开始优化 HTML 文件...');
console.log(`文件路径：${filePath}\n`);

// 检查文件是否存在
if (!fs.existsSync(filePath)) {
    console.error(`错误：文件不存在 - ${filePath}`);
    process.exit(1);
}

// 读取文件
let content = fs.readFileSync(filePath, 'utf8');
const originalSize = Buffer.byteLength(content, 'utf8');
console.log(`原始大小：${originalSize.toLocaleString()} 字节`);

// 创建备份
fs.writeFileSync(backupPath, content, 'utf8');
console.log(`✓ 已创建备份：${backupPath}\n`);

// === 开始优化 ===

// 1. 简化 lang 属性
content = content.replace(/lang="zh-CN,en,default"/g, 'lang="zh-CN"');
console.log('✓ 简化 lang 属性');

// 2. 删除 generator meta 标签
content = content.replace(/\s*<meta name="generator"[^>]*>\n?/g, '');
console.log('✓ 删除 generator meta 标签');

// 3. 删除 link 标签中的 type="image/png"
content = content.replace(/type="image\/png"\s*/g, '');
console.log('✓ 删除 favicon 的 type 属性');

// 4. 删除 script 和 style 标签中的默认 type 属性
content = content.replace(/\s+type="text\/javascript"/g, '');
content = content.replace(/\s+type="text\/css"/g, '');
console.log('✓ 删除默认的 type 属性');

// 5. 删除空的 meta 标签
content = content.replace(/<meta[^>]*content=""[^>]*>\n?/g, '');
console.log('✓ 删除空的 meta 标签');

// 6. 压缩多个连续空行为一个空行
content = content.replace(/
\s*
\s*
/g, '

');
console.log('✓ 压缩空行');

// 7. 删除行尾空格
content = content.split('\n').map(line => line.trimEnd()).join('\n');
console.log('✓ 删除行尾空格');

// 8. 删除 HTML 注释（保留重要的）
// 删除作者、版权相关的注释
content = content.replace(/<!--\s*Author:\s*.*?-->/gs, '');
content = content.replace(/<!--\s*Copyright.*?-->/gs, '');
// 删除其他普通注释
content = content.replace(/<!--(?!\[CDATA\[).*?-->/gs, '');
console.log('✓ 删除无用注释');

// 9. 删除自闭合标签末尾的斜杠（HTML5 支持）
content = content.replace(/\s*\/>/g, '>');
console.log('✓ 简化自闭合标签');

// 10. 优化 CDN 链接为协议相对 URL
content = content.replace(/https:\/\/cdn\.jsdelivr\.net/g, '//cdn.jsdelivr.net');
content = content.replace(/https:\/\/fonts\.googleapis\.com/g, '//fonts.googleapis.com');
console.log('✓ 优化 CDN 链接');

// 11. 删除重复的 class 属性值
content = content.replace(/class="([^"]*)"/g, (match, classes) => {
    const classList = classes.split(/\s+/).filter(c => c.trim());
    const uniqueClasses = [...new Set(classList)];
    return `class="${uniqueClasses.join(' ')}"`;
});
console.log('✓ 删除重复的 class 值');

// 12. 简化布尔属性
content = content.replace(/disableddisabled/g, 'disabled');
content = content.replace(/checkedchecked/g, 'checked');
content = content.replace(/selectedselected/g, 'selected');
console.log('✓ 简化布尔属性');

// 13. 再次压缩空行和空白
content = content.replace(/\n{3,}/g, '\n\n');
content = content.trim();
console.log('✓ 最终清理');

// === 优化完成 ===

const optimizedSize = Buffer.byteLength(content, 'utf8');
const reduction = ((originalSize - optimizedSize) / originalSize * 100).toFixed(2);

console.log(`\n优化后大小：${optimizedSize.toLocaleString()} 字节`);
console.log(`减少了：${reduction}%`);
console.log(`节省了：${(originalSize - optimizedSize).toLocaleString()} 字节`);

// 写回文件
try {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`\n✓ 文件已优化并保存`);
    console.log('\n🎉 优化完成！');
} catch (error) {
    console.error(`\n写入文件失败：${error}`);
    // 如果失败，恢复备份
    if (fs.existsSync(backupPath)) {
        const originalContent = fs.readFileSync(backupPath, 'utf8');
        fs.writeFileSync(filePath, originalContent, 'utf8');
        console.log('已恢复到原始版本');
    }
    process.exit(1);
}
