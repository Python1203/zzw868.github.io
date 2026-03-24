/**
 * ========================================
 * 金融 AI 组件 Tab 切换脚本
 * 功能：实现股票预测和加密货币仪表板的切换
 * ========================================
 */

(function() {
  'use strict';

  // 等待 DOM 加载完成
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    console.log('🚀 初始化金融 AI 组件...');
    
    // 获取所有 tab 按钮和内容区
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabButtons.length === 0 || tabContents.length === 0) {
      console.warn('⚠️ 未找到金融 AI 组件，跳过初始化');
      return;
    }

    // 为每个按钮添加点击事件
    tabButtons.forEach(button => {
      button.addEventListener('click', handleTabClick);
    });

    // 懒加载优化：只在切换时加载 iframe
    setupLazyLoad(tabContents);

    console.log('✅ 金融 AI 组件初始化完成');
  }

  /**
   * Tab 点击事件处理
   */
  function handleTabClick(event) {
    const clickedButton = event.currentTarget;
    const targetTab = clickedButton.dataset.tab;

    // 更新按钮状态
    updateTabButtons(clickedButton);

    // 更新内容显示
    updateTabContent(targetTab);

    // 触发自定义事件（供外部监听）
    dispatchTabChangeEvent(targetTab);
  }

  /**
   * 更新 Tab 按钮状态
   */
  function updateTabButtons(activeButton) {
    const allButtons = document.querySelectorAll('.tab-btn');
    
    allButtons.forEach(btn => {
      btn.classList.remove('active');
    });

    activeButton.classList.add('active');
  }

  /**
   * 更新 Tab 内容显示
   */
  function updateTabContent(targetTab) {
    const allContents = document.querySelectorAll('.tab-content');
    
    allContents.forEach(content => {
      content.classList.remove('active');
      
      // 如果是目标 tab，添加 active 类并标记为已加载
      if (content.id === `${targetTab}-tab`) {
        content.classList.add('active');
        content.classList.add('loaded');
      }
    });
  }

  /**
   * 懒加载设置
   */
  function setupLazyLoad(tabContents) {
    // 初始只加载第一个 tab
    tabContents.forEach((content, index) => {
      if (index === 0) {
        content.classList.add('loaded');
      } else {
        content.classList.remove('loaded');
      }
    });
  }

  /**
   * 触发自定义事件
   */
  function dispatchTabChangeEvent(tabName) {
    const event = new CustomEvent('widgetTabChange', {
      detail: { tab: tabName },
      bubbles: true
    });

    document.dispatchEvent(event);
    console.log(`📑 Tab 切换到：${tabName}`);
  }

  /**
   * 工具函数：平滑滚动到组件位置
   */
  window.scrollToWidget = function() {
    const widgetSection = document.querySelector('.widget-section');
    
    if (widgetSection) {
      widgetSection.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  };

  /**
   * 工具函数：编程式切换 Tab
   */
  window.switchWidgetTab = function(tabName) {
    const targetButton = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
    
    if (targetButton) {
      targetButton.click();
    }
  };

  /**
   * 性能优化： visibility API 检测页面可见性
   */
  let isPageVisible = true;

  document.addEventListener('visibilitychange', function() {
    isPageVisible = !document.hidden;
    
    if (isPageVisible) {
      // 页面重新可见时，刷新数据
      refreshWidgetData();
    }
  });

  /**
   * 刷新组件数据（如果实现了该方法）
   */
  function refreshWidgetData() {
    if (typeof window.refreshStockData === 'function') {
      window.refreshStockData();
    }
    
    if (typeof window.refreshCryptoData === 'function') {
      window.refreshCryptoData();
    }
  }

  /**
   * 错误处理和降级方案
   */
  window.addEventListener('error', function(event) {
    if (event.target.tagName === 'IFRAME' || 
        event.target.src.includes('stock-chart-widget') ||
        event.target.src.includes('crypto-dashboard-widget')) {
      
      console.error('❌ 组件加载失败，显示降级提示');
      showFallbackMessage(event.target);
    }
  }, true);

  /**
   * 显示降级消息
   */
  function showFallbackMessage(element) {
    const fallbackHtml = `
      <div style="
        padding: 40px;
        text-align: center;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        color: #333;
      ">
        <i class="fas fa-exclamation-triangle" style="
          font-size: 48px;
          color: #f56565;
          margin-bottom: 20px;
        "></i>
        <h3 style="font-size: 20px; margin-bottom: 10px;">组件加载失败</h3>
        <p style="color: #666;">请检查网络连接或稍后重试</p>
        <button onclick="location.reload()" style="
          margin-top: 20px;
          padding: 10px 20px;
          background: #667eea;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
        ">刷新页面</button>
      </div>
    `;

    if (element && element.parentElement) {
      element.parentElement.innerHTML = fallbackHtml;
    }
  }

  /**
   * 键盘导航支持
   */
  document.addEventListener('keydown', function(event) {
    // Alt + 1 切换到股票预测
    if (event.altKey && event.key === '1') {
      event.preventDefault();
      switchWidgetTab('stock');
    }
    
    // Alt + 2 切换到加密货币
    if (event.altKey && event.key === '2') {
      event.preventDefault();
      switchWidgetTab('crypto');
    }
  });

  console.log('🎹 快捷键已启用：Alt+1 股票预测 | Alt+2 加密货币');

})();
