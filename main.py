import os
import sys
import datetime
import requests

# 本地开发自动加载 .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- 1. 配置信息 ---
# 兼容 DEEP_SEEK_KEY（workflow 变量名）和 AI_API_KEY（.env 变量名）
DEEP_SEEK_API_KEY = (
    os.getenv("DEEP_SEEK_KEY") or
    os.getenv("AI_API_KEY")
)
POSTS_PATH = "./source/_posts"


# --- 幂等检查：判断今天是否应该运行 ---
def should_run_today():
    """
    两个条件同时满足才运行：
      1. 今天是工作日（周一至周五）
      2. 今天的文章尚未生成
    """
    now = datetime.datetime.now()

    # 周六(5)、周日(6) 不运行
    if now.weekday() >= 5:
        print(f"⏭ 今天是{['周一','周二','周三','周四','周五','周六','周日'][now.weekday()]}，跳过。")
        return False

    # 当天文章已存在则跳过（防止重复生成）
    file_path = os.path.join(POSTS_PATH, f"{now.strftime('%Y-%m-%d')}-financial-report.md")
    if os.path.exists(file_path):
        print(f"⏭ 今日文章已存在，跳过：{file_path}")
        return False

    return True


# --- 2. 抓取真实行情数据 ---
def fetch_market_data():
    """获取标普500、纳斯达克、黄金和原油的最新数据，同时返回最大涨跌幅"""
    tickers = {
        "S&P 500":   "^GSPC",
        "Nasdaq":    "^IXIC",
        "Gold":      "GC=F",
        "Crude Oil": "CL=F",
    }
    summary    = []
    max_change = 0.0   # 情绪标尺：取波动绝对值最大的涨跌幅，保留正负号

    for name, symbol in tickers.items():
        ticker = yf.Ticker(symbol)
        data   = ticker.history(period="2d")
        if len(data) >= 2:
            close_price = data['Close'].iloc[-1]
            prev_close  = data['Close'].iloc[-2]
            change_pct  = (close_price - prev_close) / prev_close * 100

            summary.append(f"{name}: {close_price:.2f} ({change_pct:+.2f}%)")

            # 取波动绝对值最大的那个指标作为“情绪标尺”
            if abs(change_pct) > abs(max_change):
                max_change = change_pct

    return "\n".join(summary), max_change


# --- 3. 调用 DeepSeek API 分析（含市场情绪判断）---
def get_ai_analysis(market_data, max_change):
    """
    根据最大波动率自动调整 AI 的语气
      max_change >= +2.0 → 🚀 狂欢模式（暴涨）
      max_change <= -2.0 → ⚠️ 预警模式（暴跌）
      其他              → 📊 稳健模式（平稳）
    """
    # 硬编码使用正确的 BASE_URL（解决环境变量加载问题）
    base_url = "https://xh.v1api.cc/v1"
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {DEEP_SEEK_API_KEY}",
    }

    # --- 动态语气逻辑 ---
    if max_change >= 2.0:
        tone_instruction = "当前市场出现大幅暴涨，语气应表现得【极度兴奋、激进】，提醒读者抓住牛市机会，分析上涨背后的核心动力。"
        style_tag = "🚀 狂欢模式"
    elif max_change <= -2.0:
        tone_instruction = "当前市场出现剧烈暴跌，语气应表现得【极其严谨、警示】，使用危机感强的词汇，提醒读者注意避险，寻找支撑位。"
        style_tag = "⚠️ 预警模式"
    else:
        tone_instruction = "当前市场波动平稳，语气应保持【冷静、专业、客观】，进行例行的技术面和基本面分析。"
        style_tag = "📊 稳健模式"

    prompt = f"""
    今日市场数据汇总：
    {market_data}

    写作要求：
    1. 风格指南：{tone_instruction}
    2. 必须包含一个符合当前氛围的文章标题。
    3. 深度解读数据，使用 Markdown 格式，包含二级标题、引用块（>）和加粗。
    4. 结尾包含风险提示与免责声明。
    """

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": f"你是一位拥有20年经验的全球财经首席评论员。当前文章标签：{style_tag}。"},
            {"role": "user",   "content": prompt},
        ],
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'], style_tag
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"AI 分析生成失败: {e}", "❌ 错误"


# --- 4. 写入 Hexo 博文 ---
def save_to_hexo(content, style_tag=""):
    now       = datetime.datetime.now()
    title     = f"AI 金融观察：{now.strftime('%Y年%m月%d日')}市场简报"
    file_name = f"{now.strftime('%Y-%m-%d')}-financial-report.md"

    header = f"""---
title: {title}
date: {now.strftime('%Y-%m-%d %H:%M:%S')}
tags: [金融, 市场分析, AI, "{style_tag}"]
categories: 财经
---

"""
    file_path = os.path.join(POSTS_PATH, file_name)

    if not os.path.exists(POSTS_PATH):
        os.makedirs(POSTS_PATH)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(header + content)
    print(f"🎉 博文已生成: {file_path}")
    print(f"🏷  市场情绪: {style_tag}")


# --- 执行主流程 ---
if __name__ == "__main__":
    if not should_run_today():
        sys.exit(0)

    print("Step 1: 正在抓取市场真实数据...")
    raw_data, max_change = fetch_market_data()
    print(raw_data)
    print(f"最大涨跌幅: {max_change:+.2f}%")

    print("\nStep 2: 正在调用 DeepSeek 进行深度分析...")
    if DEEP_SEEK_API_KEY:
        ai_content, style_tag = get_ai_analysis(raw_data, max_change)

        print("Step 3: 正在保存至 Hexo...")
        save_to_hexo(ai_content, style_tag)

        print("Step 4: 正在注入实时行情表格...")
        import subprocess
        subprocess.run([sys.executable, "tools/inject_quotes.py"], check=True)
    else:
        print("❌ 错误：未发现 API Key，请在 .env 中配置 AI_API_KEY 或 DEEP_SEEK_KEY")
