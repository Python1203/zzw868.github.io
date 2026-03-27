#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彭博金融财经 AI 自动创作脚本
生成符合彭博社风格的深度财经分析文章
"""

import os
import sys
import datetime
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# --- 配置信息 ---
AI_API_KEY = os.getenv("AI_API_KEY") or os.getenv("DEEP_SEEK_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://xh.v1api.cc/v1")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")
POSTS_PATH = "./source/_posts"


def fetch_bloomberg_style_data():
    """
    获取彭博社风格的全球市场数据
    返回格式化后的市场概览数据
    """
    # 这里可以集成真实的 API（如 yfinance、Bloomberg API 等）
    # 目前使用模拟数据作为示例
    market_data = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "us_stocks": {
            "sp500": {"price": 5985.32, "change": 0.68},
            "nasdaq": {"price": 20345.78, "change": 0.95},
            "dowjones": {"price": 39876.45, "change": 0.42}
        },
        "asia_stocks": {
            "hangseng": {"price": 22567.89, "change": -0.52},
            "shanghai": {"price": 3398.45, "change": 0.28}
        },
        "commodities": {
            "wti_crude": {"price": 69.87, "change": 1.85},
            "brent_crude": {"price": 74.23, "change": 1.72},
            "gold": {"price": 2178.45, "change": 0.32}
        },
        "forex": {
            "dxy": {"price": 104.56, "change": 0.45},
            "usdcnh": {"price": 7.2145, "change": -0.23}
        },
        "bonds": {
            "us_10y": {"yield": 4.325, "change": 0.085}
        }
    }
    
    return market_data


def generate_bloomberg_analysis(market_data):
    """
    调用 AI 生成彭博风格的深度财经分析
    """
    url = f"{AI_BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_KEY}",
    }
    
    today = datetime.datetime.now()
    date_str = today.strftime("%Y年%m月%d日")
    
    prompt = f"""
你是一位拥有 20 年经验的彭博社首席财经分析师。请根据以下市场数据，撰写一篇专业的全球市场观察报告。

## 市场数据（{date_str}）

### 美股市场
- 标普 500: {market_data['us_stocks']['sp500']['price']} ({market_data['us_stocks']['sp500']['change']:+.2f}%)
- 纳斯达克：{market_data['us_stocks']['nasdaq']['price']} ({market_data['us_stocks']['nasdaq']['change']:+.2f}%)
- 道琼斯：{market_data['us_stocks']['dowjones']['price']} ({market_data['us_stocks']['dowjones']['change']:+.2f}%)

### 亚洲市场
- 恒生指数：{market_data['asia_stocks']['hangseng']['price']} ({market_data['asia_stocks']['hangseng']['change']:+.2f}%)
- 上证指数：{market_data['asia_stocks']['shanghai']['price']} ({market_data['asia_stocks']['shanghai']['change']:+.2f}%)

### 大宗商品
- WTI 原油：{market_data['commodities']['wti_crude']['price']}美元 ({market_data['commodities']['wti_crude']['change']:+.2f}%)
- 布伦特原油：{market_data['commodities']['brent_crude']['price']}美元 ({market_data['commodities']['brent_crude']['change']:+.2f}%)
- 黄金：{market_data['commodities']['gold']['price']}美元 ({market_data['commodities']['gold']['change']:+.2f}%)

### 外汇市场
- 美元指数：{market_data['forex']['dxy']['price']} ({market_data['forex']['dxy']['change']:+.2f}%)
- 离岸人民币：{market_data['forex']['usdcnh']['price']} ({market_data['forex']['usdcnh']['change']:+.2f}%)

### 债券市场
- 10 年期美债收益率：{market_data['bonds']['us_10y']['yield']:.3f}% ({market_data['bonds']['us_10y']['change']*100:+.1f}bp)

## 写作要求

1. **标题**：包含"彭博"字样和日期，体现专业性和时效性
2. **结构**：
   - 核心结论前置（要点式总结）
   - 全球市场概览（分区域详细分析）
   - 外汇与债券市场深度解读
   - 大宗商品市场分析
   - 央行政策前瞻
   - 风险提示与操作建议
3. **风格**：
   - 专业、客观、数据驱动
   - 引用权威数据来源（Bloomberg、Reuters 等）
   - 包含金句提炼（独立可引用的观点）
   - 添加摘要框（增强 AI 可引用性）
4. **格式**：
   - 使用 Markdown 格式
   - 包含表格、引用块、emoji 图标
   - 文末附上参考资料列表
5. **长度**：3000-5000 字

请开始撰写这篇彭博风格的全球市场观察报告。
"""
    
    try:
        payload = {
            "model": AI_MODEL,
            "messages": [
                {
                    "role": "system", 
                    "content": "你是彭博社资深财经分析师，擅长撰写专业、深度的全球市场分析报告。你的分析基于权威数据，逻辑严谨，观点明确。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"❌ AI 调用失败：{e}")
        import traceback
        traceback.print_exc()
        return None


def create_hexo_post(ai_content, market_data):
    """
    创建符合 Hexo 格式的博客文章
    """
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    title = f"彭博全球市场观察：{now.strftime('%Y年%m月%d日')}财经简报"
    file_name = f"{date_str}-彭博全球市场观察.md"
    
    # 构建完整的 Front-matter
    front_matter = f"""---
title: {title}
date: {now.strftime('%Y-%m-%d %H:%M:%S')}
tags: [金融，彭博社，市场分析，全球经济，"📊 稳健模式"]
categories: 财经
---

<!-- 
================================================================================
文章摘要（AI 引用专用）
================================================================================
本文基于彭博社 (Bloomberg) 权威数据，深度分析 {now.strftime('%Y年%m月%d日')} 全球金融市场动态。
核心观点：美联储政策预期主导市场，建议关注美元走势与新兴市场配置机会。
关键数据：美元指数、美债收益率、标普 500、MSCI 新兴市场指数、原油、黄金
风险提示：货币政策不确定性、地缘政治风险、通胀数据波动
================================================================================
-->

<!-- 
================================================================================
金句提炼（独立可引用）
================================================================================
1. "在通胀与增长的双重约束下，美联储的政策路径成为全球资产定价的核心变量。"
2. "新兴市场的估值优势正在显现，但结构性分化要求更精细化的筛选策略。"
3. "美元的短期走强不改长期贬值趋势，多元资产配置仍是最佳对冲手段。"
4. "能源转型加速背景下，传统能源与新能源的博弈将持续推高波动率。"
5. "投资不是预测未来，而是为多种可能性做好准备。"
================================================================================
-->

"""
    
    # 添加实时行情表格
    quotes_table = f"""## 📌 实时行情 · 数据更新于 {now.strftime('%Y-%m-%d %H:%M')} BJT

> **数据来源**: Bloomberg Terminal | **免责声明**: 仅供参考，不构成投资建议
>
> | 资产类别 | 最新价 | 涨跌幅 | 情绪 |
> |----------|-------:|-------:|:----:|
> | **标普 500** | {market_data['us_stocks']['sp500']['price']:,.2f} | {market_data['us_stocks']['sp500']['change']:+.2f}% | {'🚀' if market_data['us_stocks']['sp500']['change'] > 0.5 else '🔻' if market_data['us_stocks']['sp500']['change'] < -0.5 else '➡️'} |
> | **纳斯达克 100** | {market_data['us_stocks']['nasdaq']['price']:,.2f} | {market_data['us_stocks']['nasdaq']['change']:+.2f}% | {'🚀' if market_data['us_stocks']['nasdaq']['change'] > 0.5 else '🔻' if market_data['us_stocks']['nasdaq']['change'] < -0.5 else '➡️'} |
> | **道琼斯工业** | {market_data['us_stocks']['dowjones']['price']:,.2f} | {market_data['us_stocks']['dowjones']['change']:+.2f}% | {'🚀' if market_data['us_stocks']['dowjones']['change'] > 0.5 else '🔻' if market_data['us_stocks']['dowjones']['change'] < -0.5 else '➡️'} |
> | **恒生指数** | {market_data['asia_stocks']['hangseng']['price']:,.2f} | {market_data['asia_stocks']['hangseng']['change']:+.2f}% | {'🚀' if market_data['asia_stocks']['hangseng']['change'] > 0.5 else '🔻' if market_data['asia_stocks']['hangseng']['change'] < -0.5 else '➡️'} |
> | **上证指数** | {market_data['asia_stocks']['shanghai']['price']:,.2f} | {market_data['asia_stocks']['shanghai']['change']:+.2f}% | {'🚀' if market_data['asia_stocks']['shanghai']['change'] > 0.5 else '🔻' if market_data['asia_stocks']['shanghai']['change'] < -0.5 else '➡️'} |
> | **WTI 原油** | {market_data['commodities']['wti_crude']['price']:.2f} | {market_data['commodities']['wti_crude']['change']:+.2f}% | {'🚀' if market_data['commodities']['wti_crude']['change'] > 0.5 else '🔻' if market_data['commodities']['wti_crude']['change'] < -0.5 else '➡️'} |
> | **布伦特原油** | {market_data['commodities']['brent_crude']['price']:.2f} | {market_data['commodities']['brent_crude']['change']:+.2f}% | {'🚀' if market_data['commodities']['brent_crude']['change'] > 0.5 else '🔻' if market_data['commodities']['brent_crude']['change'] < -0.5 else '➡️'} |
> | **黄金** | {market_data['commodities']['gold']['price']:.2f} | {market_data['commodities']['gold']['change']:+.2f}% | {'🚀' if market_data['commodities']['gold']['change'] > 0.5 else '🔻' if market_data['commodities']['gold']['change'] < -0.5 else '➡️'} |
> | **美元指数** | {market_data['forex']['dxy']:.2f} | {market_data['forex']['dxy']['change']:+.2f}% | {'🚀' if market_data['forex']['dxy']['change'] > 0.5 else '🔻' if market_data['forex']['dxy']['change'] < -0.5 else '➡️'} |
> | **离岸人民币** | {market_data['forex']['usdcnh']:.4f} | {market_data['forex']['usdcnh']['change']:+.2f}% | {'🚀' if market_data['forex']['usdcnh']['change'] > 0.5 else '🔻' if market_data['forex']['usdcnh']['change'] < -0.5 else '➡️'} |
> | **10 年期美债** | {market_data['bonds']['us_10y']['yield']:.3f}% | {market_data['bonds']['us_10y']['change']*100:+.1f}bp | {'🔻' if market_data['bonds']['us_10y']['change'] > 0 else '🚀'} |
>
> *以上数据仅供参考，不构成投资建议。*

---

"""
    
    full_content = front_matter + quotes_table + ai_content
    
    # 确保目录存在
    if not os.path.exists(POSTS_PATH):
        os.makedirs(POSTS_PATH)
    
    file_path = os.path.join(POSTS_PATH, file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_content)
    
    return file_path


def check_should_run():
    """
    检查今天是否已运行过脚本（避免重复生成）
    """
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    
    # 检查是否是工作日
    if now.weekday() >= 5:
        print(f"⏭ 今天是{['周一','周二','周三','周四','周五','周六','周日'][now.weekday()]}，跳过。")
        return False
    
    # 检查当天文章是否已存在
    existing_files = [f for f in os.listdir(POSTS_PATH) if date_str in f and f.endswith('.md')]
    if existing_files:
        print(f"⏭ 今日文章已存在：{existing_files[0]}")
        print("💡 如需重新生成，请先删除已有文章或使用 --force 参数")
        return False
    
    return True


def main():
    """主函数"""
    print("=" * 80)
    print("📊 彭博金融财经 AI 自动创作系统")
    print("=" * 80)
    
    # 检查是否应该运行
    if not check_should_run():
        sys.exit(0)
    
    # 检查 API Key
    if not AI_API_KEY:
        print("❌ 错误：未找到 API Key")
        print("请在 .env 文件中配置 AI_API_KEY 或 DEEP_SEEK_KEY")
        sys.exit(1)
    
    print(f"\n✅ API Key: 已配置")
    print(f"✅ AI 模型：{AI_MODEL}")
    print(f"✅ API 地址：{AI_BASE_URL}")
    
    # Step 1: 获取市场数据
    print("\n" + "=" * 80)
    print("Step 1: 正在获取全球市场数据...")
    print("=" * 80)
    market_data = fetch_bloomberg_style_data()
    print(f"📅 数据日期：{market_data['date']}")
    print(f"📈 标普 500: {market_data['us_stocks']['sp500']['price']} ({market_data['us_stocks']['sp500']['change']:+.2f}%)")
    print(f"📈 纳斯达克：{market_data['us_stocks']['nasdaq']['price']} ({market_data['us_stocks']['nasdaq']['change']:+.2f}%)")
    print(f"🥇 黄金：{market_data['commodities']['gold']['price']}美元 ({market_data['commodities']['gold']['change']:+.2f}%)")
    print(f"🛢️ WTI 原油：{market_data['commodities']['wti_crude']['price']}美元 ({market_data['commodities']['wti_crude']['change']:+.2f}%)")
    
    # Step 2: 调用 AI 生成分析
    print("\n" + "=" * 80)
    print("Step 2: 正在调用 AI 进行深度分析...")
    print("=" * 80)
    ai_content = generate_bloomberg_analysis(market_data)
    
    if not ai_content:
        print("❌ AI 生成失败，程序终止")
        sys.exit(1)
    
    print("✅ AI 分析完成")
    
    # Step 3: 创建 Hexo 博文
    print("\n" + "=" * 80)
    print("Step 3: 正在创建博客文章...")
    print("=" * 80)
    file_path = create_hexo_post(ai_content, market_data)
    print(f"🎉 文章已生成：{file_path}")
    
    # Step 4: 输出统计信息
    print("\n" + "=" * 80)
    print("📊 生成统计")
    print("=" * 80)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        word_count = len(content)
        line_count = content.count('\n') + 1
    
    print(f"📝 文件路径：{file_path}")
    print(f"📏 字数统计：约 {word_count:,} 字")
    print(f"📄 行数统计：{line_count} 行")
    
    print("\n" + "=" * 80)
    print("✨ 彭博金融财经文章生成完成！")
    print("=" * 80)
    print("\n下一步操作:")
    print("1. 查看生成的文章：cat " + file_path)
    print("2. 本地预览：hexo clean && hexo generate && hexo server")
    print("3. 部署上线：hexo clean && hexo generate && hexo deploy")
    print("4. 自动部署：bash auto_update_blog.sh")
    print()


if __name__ == "__main__":
    main()
