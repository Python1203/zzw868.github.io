/**
 * AI 聊天助手自动嵌入工具
 * 功能：自动为博客主页注入 AI 聊天助手组件
 */

const fs = require('fs');
const path = require('path');

// 配置
const config = {
  // 目标文件：博客主页
  targetFile: 'index.html',
  
  // AI 聊天助手组件文件
  chatComponent: 'ai-chat.html',
  
  // 输出目录
  outputDir: '.',
  
  // 是否仅在首页显示
  onlyHome: true,
  
  // 显示模式：'button' (悬浮按钮) | 'embed' (嵌入式) | 'sidebar' (侧边栏)
  displayMode: 'button'
};

/**
 * 读取并处理 AI 聊天助手 HTML
 */
function extractChatComponent() {
  console.log('🚀 开始提取 AI 聊天助手组件...\n');
  
  const chatPath = path.join(config.outputDir, config.chatComponent);
  
  if (!fs.existsSync(chatPath)) {
    console.log(`❌ 文件不存在：${chatPath}`);
    return null;
  }
  
  console.log(`✓ 读取文件：${chatPath}`);
  
  const chatContent = fs.readFileSync(chatPath, 'utf8');
  
  // 提取 CSS 样式
  const styleMatch = chatContent.match(/<style>([\s\S]*?)<\/style>/);
  const styles = styleMatch ? styleMatch[1] : '';
  
  // 提取 JavaScript
  const scriptMatch = chatContent.match(/<script>([\s\S]*?)<\/script>/i);
  const scripts = scriptMatch ? scriptMatch[1] : '';
  
  // 提取 HTML 结构 (container 部分)
  const containerMatch = chatContent.match(/(<div class="container"[\s\S]*?<\/div>\s*<\/div>\s*<\/div>)/);
  const containerHTML = containerMatch ? containerMatch[1] : '';
  
  return {
    styles,
    scripts,
    html: containerHTML,
    fullContent: chatContent
  };
}

/**
 * 生成注入代码
 */
function generateInjectionCode(component) {
  const injection = {
    css: `
<!-- AI Chat Component Styles -->
<style>
  /* AI 聊天助手悬浮按钮 */
  .ai-chat-float-btn {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    box-shadow: 0 8px 24px rgba(102,126,234,0.4);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: white;
    z-index: 9999;
    transition: all 0.3s ease;
    animation: pulse 2s infinite;
  }
  
  .ai-chat-float-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 12px 32px rgba(102,126,234,0.6);
  }
  
  @keyframes pulse {
    0%, 100% {
      box-shadow: 0 8px 24px rgba(102,126,234,0.4);
    }
    50% {
      box-shadow: 0 8px 32px rgba(102,126,234,0.7);
    }
  }
  
  /* AI 聊天窗口 */
  .ai-chat-modal {
    position: fixed;
    bottom: 100px;
    right: 30px;
    width: 400px;
    max-width: calc(100vw - 60px);
    background: white;
    border-radius: 16px;
    box-shadow: 0 12px 48px rgba(0,0,0,0.2);
    z-index: 9998;
    display: none;
    overflow: hidden;
    animation: slideInRight 0.3s ease-out;
  }
  
  .ai-chat-modal.active {
    display: block;
  }
  
  @keyframes slideInRight {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  /* 关闭按钮 */
  .ai-chat-close {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 32px;
    height: 32px;
    background: rgba(0,0,0,0.1);
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: #666;
    transition: all 0.2s ease;
    z-index: 10;
  }
  
  .ai-chat-close:hover {
    background: rgba(0,0,0,0.2);
    color: #333;
  }
  
  /* 简化版聊天容器 */
  .ai-chat-container {
    height: 500px;
    display: flex;
    flex-direction: column;
  }
  
  .ai-chat-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 16px 20px;
    font-weight: 700;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .ai-chat-messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    background: #f9f9f9;
  }
  
  .ai-chat-input {
    border-top: 1px solid #e0e0e0;
    padding: 15px 20px;
    display: flex;
    gap: 10px;
    background: white;
  }
  
  .ai-chat-input input {
    flex: 1;
    padding: 10px 16px;
    border-radius: 20px;
    border: 2px solid #e0e0e0;
    outline: none;
    transition: all 0.3s ease;
  }
  
  .ai-chat-input input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
  }
  
  .ai-chat-input button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;
    padding: 10px 20px;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
  }
  
  .ai-chat-input button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(102,126,234,0.4);
  }
  
  /* 响应式 */
  @media (max-width: 768px) {
    .ai-chat-float-btn {
      bottom: 20px;
      right: 20px;
      width: 50px;
      height: 50px;
      font-size: 24px;
    }
    
    .ai-chat-modal {
      bottom: 80px;
      right: 20px;
      width: calc(100vw - 40px);
    }
  }
</style>
`,
    
    html: `
<!-- AI Chat Component -->
<div class="ai-chat-float-btn" onclick="toggleAIChat()" title="AI 智能助手">
  🤖
</div>

<div class="ai-chat-modal" id="aiChatModal">
  <div class="ai-chat-close" onclick="toggleAIChat()">×</div>
  <div class="ai-chat-container">
    <div class="ai-chat-header">
      <span>💬 AI 智能聊天助手</span>
    </div>
    <div class="ai-chat-messages" id="aiChatMessages">
      <div style="text-align: center; color: #999; margin-top: 40px;">
        <div style="font-size: 48px; margin-bottom: 10px;">🤖</div>
        <div>点击下面输入框开始对话</div>
        <div style="font-size: 0.85rem; margin-top: 8px;">支持 OpenAI、百度文心等多个 AI 服务</div>
      </div>
    </div>
    <form class="ai-chat-input" onsubmit="sendAIMessage(event)">
      <input type="text" id="aiChatInput" placeholder="请输入消息..." autocomplete="off" />
      <button type="submit">发送</button>
    </form>
  </div>
</div>
`,
    
    js: `
<!-- AI Chat Component Logic -->
<script>
  // AI 聊天助手配置
  const AI_CHAT_CONFIG = {
    OPENAI_KEY: 'sk-V8hcmOdmpvRS5uOogqDAcijxZpu2Oc6uI7gQbj3xmV59hDv4',
    OPENAI_BASE: 'https://api.chatanywhere.tech/v1/chat/completions',
    BAIDU_KEY: 'bce-v3/ALTAK-xNWWCIP6mLrKFV2KopRYy/a91d82e00aa2894b60900978be66a57d54d11099',
    BAIDU_BASE: 'https://qianfan.baidubce.com/v2/chat/completions',
    HF_TOKEN: 'YOUR_HF_TOKEN_HERE',
    HF_BASE: 'https://router.huggingface.co/v1/chat/completions'
  };
  
  let aiChatHistory = [];
  const MAX_AI_HISTORY = 6;
  
  // 切换聊天窗口
  function toggleAIChat() {
    const modal = document.getElementById('aiChatModal');
    modal.classList.toggle('active');
    
    if (modal.classList.contains('active')) {
      setTimeout(() => {
        document.getElementById('aiChatInput').focus();
      }, 300);
    }
  }
  
  // 添加消息到聊天
  function addAIMessage(text, sender) {
    const messagesDiv = document.getElementById('aiChatMessages');
    const messageRow = document.createElement('div');
    messageRow.style.cssText = \`margin-bottom: 16px; display: flex; \${sender === 'user' ? 'justify-content: flex-end;' : ''}\`;
    
    const bubble = document.createElement('div');
    bubble.style.cssText = \`
      max-width: 75%;
      padding: 12px 16px;
      border-radius: 16px;
      \${sender === 'user' 
        ? 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;' 
        : 'background: white; color: #333; border: 1px solid #e0e0e0;'}
    \`;
    bubble.textContent = text;
    
    messageRow.appendChild(bubble);
    messagesDiv.appendChild(messageRow);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }
  
  // 发送消息
  async function sendAIMessage(event) {
    event.preventDefault();
    const input = document.getElementById('aiChatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 添加用户消息
    addAIMessage(message, 'user');
    input.value = '';
    
    // 显示加载状态
    const messagesDiv = document.getElementById('aiChatMessages');
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'aiLoading';
    loadingDiv.style.cssText = 'margin-bottom: 16px; color: #999; font-style: italic;';
    loadingDiv.textContent = 'AI 正在思考...';
    messagesDiv.appendChild(loadingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // 调用 AI API
    try {
      const reply = await callAIService(message);
      
      // 移除加载提示
      const loadingElem = document.getElementById('aiLoading');
      if (loadingElem) loadingElem.remove();
      
      // 添加 AI 回复
      addAIMessage(reply, 'ai');
      
      // 更新历史记录
      aiChatHistory.push({ role: 'user', content: message });
      aiChatHistory.push({ role: 'assistant', content: reply });
      if (aiChatHistory.length > MAX_AI_HISTORY * 2) {
        aiChatHistory.shift();
      }
    } catch (error) {
      const loadingElem = document.getElementById('aiLoading');
      if (loadingElem) loadingElem.remove();
      
      addAIMessage('❌ 出错了：' + error.message, 'ai');
    }
  }
  
  // 调用 AI 服务
  async function callAIService(message) {
    // 默认使用 OpenAI
    const url = AI_CHAT_CONFIG.OPENAI_BASE;
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + AI_CHAT_CONFIG.OPENAI_KEY
    };
    
    const msgs = [
      { role: 'system', content: '你是一个有用的 AI 助手，回答简洁、准确。' },
      ...aiChatHistory,
      { role: 'user', content: message }
    ];
    
    const body = JSON.stringify({
      model: 'gpt-4',
      messages: msgs,
      max_tokens: 1000
    });
    
    const resp = await fetch(url, { method: 'POST', headers, body });
    const data = await resp.json();
    
    if (!resp.ok) {
      throw new Error(data.error?.message || '请求失败');
    }
    
    return data.choices?.[0]?.message?.content?.trim() || '（无回复）';
  }
  
  // 支持 Enter 键发送
  document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('aiChatInput');
    if (input) {
      input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          sendAIMessage({ preventDefault: () => {} });
        }
      });
    }
  });
</script>
`
  };
  
  return injection;
}

/**
 * 注入到目标文件
 */
function injectToTarget() {
  console.log('\\n📥 开始注入到目标文件...\\n');
  
  const targetPath = path.join(config.outputDir, config.targetFile);
  
  if (!fs.existsSync(targetPath)) {
    console.log(`❌ 目标文件不存在：${targetPath}`);
    return;
  }
  
  console.log(`✓ 读取目标文件：${targetPath}`);
  
  let content = fs.readFileSync(targetPath, 'utf8');
  
  // 生成注入代码
  const injection = generateInjectionCode(null);
  
  // 在 </head> 前注入 CSS
  const cssInjection = injection.css;
  content = content.replace('</head>', cssInjection + '\\n</head>');
  
  // 在 </body> 前注入 HTML 和 JS
  const htmlInjection = injection.html;
  const jsInjection = injection.js;
  content = content.replace('</body>', htmlInjection + '\\n' + jsInjection + '\\n</body>');
  
  // 保存修改后的文件
  const outputPath = path.join(config.outputDir, 'index-with-ai-chat.html');
  fs.writeFileSync(outputPath, content, 'utf8');
  
  console.log(`✓ 已保存到：${outputPath}`);
  console.log('\\n✅ AI 聊天助手注入完成!');
  console.log('\\n💡 提示:');
  console.log('   - 打开 index-with-ai-chat.html 查看效果');
  console.log('   - 点击右下角的 🤖 按钮打开聊天窗口');
  console.log('   - 如需自定义样式，请修改 generateInjectionCode 函数\\n');
}

// 执行
injectToTarget();
