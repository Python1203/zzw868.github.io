#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用百度文心 API 快速测试
"""

import requests
import json
import os

# 你的 API Key（从百度千帆控制台获取）
# 访问：https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application
# 注意：AK 和 SK 应该是纯字母数字，没有斜杠

# TODO: 请替换为你实际的 AK 和 SK
API_KEY = 'YOUR_ACTUAL_API_KEY'  # 例如：'xxxxxxxxxxxxxxxxxxxxxx'
SECRET_KEY = 'YOUR_ACTUAL_SECRET_KEY'  # 例如：'xxxxxxxxxxxxxxxxxxxxxx'

def get_access_token():
    """获取访问令牌"""
    url = f"https://qianfan.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}"
    
    response = requests.post(url)
    result = response.json()
    
    if 'access_token' in result:
        print(f"✅ 成功获取 Access Token: {result['access_token'][:20]}...")
        return result['access_token']
    else:
        print(f"❌ 获取 Token 失败：{result}")
        return None

def test_chat(access_token):
    """测试对话"""
    url = f"https://qianfan.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "你好，请介绍一下自己"
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    result = response.json()
    
    print("\n📝 响应结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if 'result' in result:
        print(f"\n✅ AI 回复：{result['result']}")
        return True
    else:
        print(f"\n❌ 调用失败：{result}")
        return False

if __name__ == "__main__":
    print("🚀 测试百度文心 API...\n")
    
    # Step 1: 获取 Token
    access_token = get_access_token()
    
    if access_token:
        # Step 2: 测试对话
        print("\n🤖 开始测试对话...\n")
        test_chat(access_token)
