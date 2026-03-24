#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复加密货币仪表板组件的 CSP 和依赖问题
"""

import os

def fix_crypto_dashboard():
    file_path = '/Users/zzw868/PycharmProjects/zzw868.github.io/source/components/crypto-dashboard-widget.html'
    
    if not os.path.exists(file_path):
        print(f'❌ 文件不存在：{file_path}')
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换旧的 script 标签
    old_pattern = r'''<script src="https://unpkg\.com/vue@3/dist/vue\.global\.js"></script>\s*
    <script src="https://unpkg\.com/pinia@2/dist/pinia\.js"></script>\s*
    <script src="https://cdn\.jsdelivr\.net/npm/echarts@5/dist/echarts\.min\.js"></script>\s*
    <!-- 金融数据服务 -->\s*
    <script src="/js/financial-data-service\.js"></script>\s*
    <!-- Binance WebSocket 服务 -->\s*
    <script src="/js/binance-service\.js"></script>'''
    
    new_scripts = '''<!-- 使用生产版本的 Vue 和 Pinia，解决 CSP 和兼容性问题 -->
    <script src="https://unpkg.com/vue@3.4.21/dist/vue.global.prod.js"></script>
    <script src="https://unpkg.com/pinia@2.1.7/dist/pinia.iife.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>'''
    
    # 使用正则表达式替换
    new_content = re.sub(old_pattern, new_scripts, content, flags=re.MULTILINE)
    
    if new_content == content:
        print('⚠️  未找到需要替换的内容，可能已经修复')
        # 检查是否已经是新版本
        if 'vue@3.4.21/dist/vue.global.prod.js' in content:
            print('✅ 文件已经使用正确的 Vue 生产版本')
        if 'pinia@2.1.7/dist/pinia.iife.min.js' in content:
            print('✅ 文件已经使用正确的 Pinia IIFE 版本')
        return False
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('✅ 文件已成功修复')
    print('📝 修改内容：')
    print('  - Vue: development → production (vue.global.prod.js)')
    print('  - Pinia: UMD → IIFE (pinia.iife.min.js)')
    print('  - ECharts: 5.x → 5.5.0')
    print('  - 移除外部 JS 依赖（financial-data-service.js, binance-service.js）')
    
    return True

if __name__ == '__main__':
    import re
    fix_crypto_dashboard()
