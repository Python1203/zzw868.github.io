#!/usr/bin/env node

/**
 * SEO 自动提交脚本
 * 将新页面/文章链接提交到百度、Bing 等搜索引擎
 * 
 * 使用方法：
 * 1. 配置环境变量或使用配置文件：
 *    - BDU_API_TOKEN: 百度站长平台 API Token
 *    - BING_API_KEY: Bing Webmaster Tools API Key
 * 
 * 2. 运行：node scripts/seo-submit.js [urls...]
 *    或：npm run seo-submit
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// 配置
const CONFIG = {
  // 百度站长平台配置
  baidu: {
    site: 'https://zzw868.github.io',
    apiToken: process.env.BDU_API_TOKEN || '',
    enabled: !!process.env.BDU_API_TOKEN
  },
  
  // Bing Webmaster Tools 配置
  bing: {
    site: 'https://zzw868.github.io',
    apiKey: process.env.BING_API_KEY || '',
    enabled: !!process.env.BING_API_KEY
  },
  
  // Google Search Console (通过 Indexing API)
  google: {
    enabled: false, // 需要 Service Account，暂不启用
  }
};

// 从 public 目录提取所有 HTML 页面链接
function extractUrlsFromPublicDir() {
  const publicDir = path.join(__dirname, '..', 'public');
  const urls = [];
  const baseUrl = CONFIG.baidu.site;
  
  function walkDir(dir) {
    if (!fs.existsSync(dir)) return;
    
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory()) {
        walkDir(filePath);
      } else if (file.endsWith('.html') || file === 'index.html') {
        // 转换为 URL 路径
        let relativePath = path.relative(publicDir, filePath);
        let urlPath = relativePath.replace(/\\/g, '/');
        
        // 处理 index.html
        if (urlPath === 'index.html') {
          urlPath = '';
        } else if (urlPath.endsWith('/index.html')) {
          urlPath = urlPath.replace('/index.html', '/');
        }
        
        const fullUrl = `${baseUrl}/${urlPath}`;
        urls.push(fullUrl);
      }
    });
  }
  
  walkDir(publicDir);
  return urls;
}

// 从 sitemap.xml 提取 URL
function extractUrlsFromSitemap() {
  const sitemapPath = path.join(__dirname, '..', 'public', 'sitemap.xml');
  const urls = [];
  
  if (!fs.existsSync(sitemapPath)) {
    console.log('⚠️  sitemap.xml 不存在，跳过');
    return urls;
  }
  
  const content = fs.readFileSync(sitemapPath, 'utf-8');
  const urlMatches = content.match(/<loc>(.*?)<\/loc>/g);
  
  if (urlMatches) {
    urlMatches.forEach(match => {
      const url = match.replace('<loc>', '').replace('</loc>', '');
      urls.push(url);
    });
  }
  
  return urls;
}

// 提交到百度站长平台
function submitToBaidu(urls) {
  return new Promise((resolve, reject) => {
    if (!CONFIG.baidu.enabled) {
      console.log('❌ 百度提交已禁用（缺少 BDU_API_TOKEN）');
      resolve({ success: false, message: 'API Token 未配置' });
      return;
    }
    
    const apiUrl = `https://data.zz.baidu.com/urls?site=${CONFIG.baidu.site}&token=${CONFIG.baidu.apiToken}`;
    
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'text/plain',
        'User-Agent': 'curl/7.12.1'
      }
    };
    
    const req = https.request(apiUrl, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          console.log('✅ 百度提交结果:', result);
          resolve(result);
        } catch (e) {
          console.error('❌ 百度提交失败:', data);
          reject(e);
        }
      });
    });
    
    req.on('error', (e) => {
      console.error('❌ 百度请求错误:', e.message);
      reject(e);
    });
    
    // 批量提交，每次最多 2000 条
    const batchUrls = urls.slice(0, 2000);
    req.write(batchUrls.join('\n'));
    req.end();
  });
}

// 提交到 Bing Webmaster Tools
function submitToBing(urls) {
  return new Promise((resolve, reject) => {
    if (!CONFIG.bing.enabled) {
      console.log('❌ Bing 提交已禁用（缺少 BING_API_KEY）');
      resolve({ success: false, message: 'API Key 未配置' });
      return;
    }
    
    const apiUrl = `https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey=${CONFIG.bing.apiKey}`;
    
    const postData = JSON.stringify({
      siteUrl: CONFIG.bing.site,
      urlList: urls
    });
    
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };
    
    const req = https.request(apiUrl, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          console.log('✅ Bing 提交结果:', result);
          resolve(result);
        } catch (e) {
          console.error('❌ Bing 提交失败:', data);
          reject(e);
        }
      });
    });
    
    req.on('error', (e) => {
      console.error('❌ Bing 请求错误:', e.message);
      reject(e);
    });
    
    req.write(postData);
    req.end();
  });
}

// 主函数
async function main() {
  console.log('🚀 开始 SEO 自动提交...\n');
  
  // 获取要提交的 URL
  let urls = [];
  
  // 优先从 sitemap.xml 获取
  if (fs.existsSync(path.join(__dirname, '..', 'public', 'sitemap.xml'))) {
    console.log('📄 从 sitemap.xml 提取 URL...');
    urls = extractUrlsFromSitemap();
  }
  
  // 如果 sitemap 为空，则扫描 public 目录
  if (urls.length === 0) {
    console.log('📁 扫描 public 目录获取 URL...');
    urls = extractUrlsFromPublicDir();
  }
  
  // 去重
  urls = [...new Set(urls)];
  
  console.log(`📊 共找到 ${urls.length} 个 URL\n`);
  
  if (urls.length === 0) {
    console.log('⚠️  没有找到可提交的 URL');
    return;
  }
  
  // 提交到各个搜索引擎
  const results = {
    baidu: null,
    bing: null
  };
  
  // 百度提交
  console.log('\n🔍 提交到百度...');
  try {
    results.baidu = await submitToBaidu(urls);
  } catch (e) {
    console.error('百度提交出错:', e.message);
  }
  
  // Bing 提交
  console.log('\n🔍 提交到 Bing...');
  try {
    results.bing = await submitToBing(urls);
  } catch (e) {
    console.error('Bing 提交出错:', e.message);
  }
  
  // 输出总结
  console.log('\n' + '='.repeat(50));
  console.log('📋 提交总结');
  console.log('='.repeat(50));
  console.log(`总 URL 数：${urls.length}`);
  console.log(`百度：${results.baidu?.success ? '✅ 成功' : '⚠️  未成功'}`);
  console.log(`Bing: ${results.bing?.success ? '✅ 成功' : '⚠️  未成功'}`);
  console.log('='.repeat(50));
}

// 运行
main().catch(console.error);
