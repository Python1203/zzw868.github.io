/**
 * Hexo 博客优化插件
 * 功能：自动为博客文章添加 React 组件支持
 */

const fs = require('fs');
const path = require('path');

// 配置
const config = {
  // 需要注入的文章目录
  targetDir: '2021/05/20/【财经期刊FM-Radio｜2021 年 05 月 20 日】',
  
  // React 组件文件
  reactComponent: 'test-stock-chart.html',
  
  // 输出目录
  outputDir: 'public'
};

/**
 * 读取 HTML 文件并注入 React 组件
 */
function injectReactComponent() {
  console.log('🚀 开始注入 React 组件...\n');
  
  const indexPath = path.join(config.targetDir, 'index.html');
  
  if (!fs.existsSync(indexPath)) {
    console.log(`❌ 文件不存在：${indexPath}`);
    return;
  }
  
  console.log(`✓ 读取文件：${indexPath}`);
  
  let content = fs.readFileSync(indexPath, 'utf8');
  
  // 在 </head> 前注入 React 相关资源
  const reactResources = `
    <!-- React Component Resources -->
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/recharts/umd/Recharts.js"></script>
    <link rel="stylesheet" href="https://cdn.tailwindcss.com">
`;
  
  content = content.replace('</head>', reactResources + '\n</head>');
  
  // 在文章内容后添加 React 组件容器
  const componentContainer = `
    <!-- React Stock Chart Component -->
    <div id="react-stock-chart" style="margin-top: 40px;"></div>
    <script>
      // 延迟加载确保 DOM 已准备好
      setTimeout(() => {
        console.log('Loading React Stock Chart Component...');
        // 这里可以动态加载组件
      }, 1000);
    </script>
`;
  
  // 查找文章正文结束位置并插入组件
  const postBodyEnd = content.indexOf('</article>');
  if (postBodyEnd !== -1) {
    content = content.slice(0, postBodyEnd) + componentContainer + content.slice(postBodyEnd);
    console.log('✓ React 组件容器已注入');
  }
  
  // 写入到 public 目录
  const outputPath = path.join(config.outputDir, config.targetDir, 'index.html');
  
  // 创建目录（如果不存在）
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
    console.log(`✓ 创建目录：${outputDir}`);
  }
  
  fs.writeFileSync(outputPath, content, 'utf8');
  console.log(`✓ 文件已写入：${outputPath}\n`);
  
  console.log('✅ React 组件注入完成！\n');
}

/**
 * 批量处理所有文章
 */
function processAllPosts() {
  console.log('📦 批量处理博客文章...\n');
  
  const years = ['2020', '2021'];
  
  years.forEach(year => {
    const yearDir = path.join(year);
    if (!fs.existsSync(yearDir)) return;
    
    const months = fs.readdirSync(yearDir)
      .filter(item => fs.statSync(path.join(yearDir, item)).isDirectory());
    
    months.forEach(month => {
      const monthDir = path.join(yearDir, month);
      const days = fs.readdirSync(monthDir)
        .filter(item => fs.statSync(path.join(monthDir, item)).isDirectory());
      
      days.forEach(day => {
        const dayDir = path.join(monthDir, day);
        const indexFile = path.join(dayDir, 'index.html');
        
        if (fs.existsSync(indexFile)) {
          console.log(`找到文章：${indexFile}`);
          // 可以在这里调用 injectReactComponent 处理每篇文章
        }
      });
    });
  });
  
  console.log('\n✅ 批量处理完成！');
}

// 执行
if (require.main === module) {
  injectReactComponent();
  // processAllPosts(); // 如需批量处理，取消注释
}

module.exports = { injectReactComponent, processAllPosts };
