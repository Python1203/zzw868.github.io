#!/usr/bin/env python3
"""
scripts/generate_post.py

数据来源：
  - AkShare  : A 股指数、人民币汇率、CPI
  - yfinance : 港股、美股、大宗商品、加密货币

环境变量（GitHub Secrets 或本地 .env）：
  AI_API_KEY   — 必填，DeepSeek / OpenAI API Key
  AI_BASE_URL  — 可选，默认 https://api.deepseek.com/v1
  AI_MODEL     — 可选，默认 deepseek-chat
"""

import os
import textwrap
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env", override=False)
except ImportError:
    pass

import requests
import yfinance as yf

# ── 配置 ──────────────────────────────────────────────────────────────────────
API_KEY  = os.environ.get("AI_API_KEY") or os.environ.get("LLM_API_KEY") or ""
if not API_KEY:
    raise EnvironmentError(
        "未找到 API Key，请在 GitHub Secrets 或 .env 中配置 AI_API_KEY。"
    )
BASE_URL = os.environ.get("AI_BASE_URL") or os.environ.get("LLM_BASE_URL") or "https://api.deepseek.com/v1"
MODEL    = os.environ.get("AI_MODEL")    or os.environ.get("LLM_MODEL")    or "deepseek-chat"

POSTS_DIR = Path(__file__).parent.parent / "source" / "_posts"
POSTS_DIR.mkdir(parents=True, exist_ok=True)

TODAY = datetime.now().strftime("%Y-%m-%d")
NOW   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── 工具函数 ──────────────────────────────────────────────────────────────────
def _yf_quote(ticker: str) -> dict:
    """拉取单个 yfinance ticker 的最新价和涨跌幅，失败返回空 dict。"""
    try:
        info = yf.Ticker(ticker).fast_info
        price  = float(info.last_price)
        prev   = float(info.previous_close)
        change = (price - prev) / prev * 100 if prev else 0.0
        return {"price": price, "change": change}
    except Exception:
        return {}


# ── 1. 拉取全量金融数据 ────────────────────────────────────────────────────────
def fetch_market_data() -> dict:
    data = {}

    # ── A 股三大指数（AkShare）────────────────────────────────────────────────
    try:
        idx = ak.stock_zh_index_spot_em()
        targets = {"上证指数": "000001", "深证成指": "399001", "创业板指": "399006"}
        a_indices = {}
        for name, code in targets.items():
            row = idx[idx["代码"] == code]
            if not row.empty:
                r = row.iloc[0]
                a_indices[name] = {
                    "price":  float(r["最新价"]),
                    "change": float(r["涨跌幅"]),
                }
        data["a_indices"] = a_indices
    except Exception as e:
        print(f"[WARN] A股指数获取失败: {e}")
        data["a_indices"] = {}

    # ── 港股 + 美股指数（yfinance）────────────────────────────────────────────
    global_map = {
        "恒生指数":   "^HSI",
        "标普500":    "^GSPC",
        "纳斯达克":   "^IXIC",
        "道琼斯":     "^DJI",
        "日经225":    "^N225",
    }
    global_indices = {}
    for name, ticker in global_map.items():
        q = _yf_quote(ticker)
        if q:
            global_indices[name] = q
    data["global_indices"] = global_indices

    # ── 大宗商品（yfinance）───────────────────────────────────────────────────
    commodity_map = {
        "黄金($/oz)":   "GC=F",
        "原油($/桶)":   "CL=F",
        "白银($/oz)":   "SI=F",
    }
    commodities = {}
    for name, ticker in commodity_map.items():
        q = _yf_quote(ticker)
        if q:
            commodities[name] = q
    data["commodities"] = commodities

    # ── 加密货币（yfinance）───────────────────────────────────────────────────
    crypto_map = {
        "BTC/USDT": "BTC-USD",
        "ETH/USDT": "ETH-USD",
    }
    crypto = {}
    for name, ticker in crypto_map.items():
        q = _yf_quote(ticker)
        if q:
            crypto[name] = q
    data["crypto"] = crypto

    # ── 人民币汇率（AkShare）──────────────────────────────────────────────────
    try:
        fx = ak.currency_boc_sina()
        fx_map = {}
        for _, row in fx.iterrows():
            name = str(row.get("货币名称", ""))
            if "美元" in name:
                fx_map["USD/CNY"] = str(row.get("现汇买入价", ""))
            elif "欧元" in name:
                fx_map["EUR/CNY"] = str(row.get("现汇买入价", ""))
            elif "日元" in name:
                fx_map["JPY/CNY"] = str(row.get("现汇买入价", ""))
        data["forex"] = fx_map
    except Exception as e:
        print(f"[WARN] 汇率获取失败: {e}")
        data["forex"] = {}

    # ── 宏观：CPI（AkShare）───────────────────────────────────────────────────
    try:
        cpi = ak.macro_china_cpi_monthly()
        latest = cpi.iloc[-1]
        data["cpi"] = {"date": str(latest.iloc[0]), "value": str(latest.iloc[1])}
    except Exception as e:
        print(f"[WARN] CPI 获取失败: {e}")
        data["cpi"] = {}

    return data


# ── 2. 构造 Prompt ─────────────────────────────────────────────────────────────
def _fmt(items: dict) -> str:
    if not items:
        return "  - 数据暂不可用"
    return "\n".join(
        f"  - {k}：{v['price']:.2f}（{v['change']:+.2f}%）"
        for k, v in items.items()
    )

def _fmt_fx(items: dict) -> str:
    if not items:
        return "  - 数据暂不可用"
    return "\n".join(f"  - {k}：{v}" for k, v in items.items())


def build_prompt(data: dict) -> str:
    cpi = data.get("cpi", {})
    cpi_text = (
        f"{cpi.get('date', 'N/A')} CPI 同比 {cpi.get('value', 'N/A')}%"
        if cpi else "数据暂不可用"
    )

    return textwrap.dedent(f"""
        你是一位专业的全球财经评论员，擅长深度分析 A 股、港股、美股及宏观经济联动关系。
        请根据以下今日（{TODAY}）实时金融数据，撰写一篇深度财经评论文章。

        【A 股指数】
        {_fmt(data.get('a_indices', {}))}

        【全球指数（港股/美股/日股）】
        {_fmt(data.get('global_indices', {}))}

        【大宗商品】
        {_fmt(data.get('commodities', {}))}

        【加密货币】
        {_fmt(data.get('crypto', {}))}

        【人民币汇率】
        {_fmt_fx(data.get('forex', {}))}

        【宏观数据】
          - {cpi_text}

        【写作要求】
        1. 风格：专业财经评论员，逻辑严谨，有观点有依据，避免口水话
        2. 结构：必须包含以下五个 ## 二级标题：
           「全球市场概览」「A股深度分析」「大宗商品与加密货币」「汇率与宏观」「风险提示与操作建议」
        3. 字数：1000～1500 字
        4. 格式：纯 Markdown，不要输出 Front-matter
        5. 文末加免责声明：> 本文由 AI 自动生成，数据来源 AkShare & Yahoo Finance，仅供参考，不构成投资建议。
    """).strip()


# ── 3. 调用 LLM ────────────────────────────────────────────────────────────────
def call_llm(prompt: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model":       MODEL,
            "messages":    [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens":  2500,
        },
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# ── 4. 生成 Hexo Markdown 文件 ─────────────────────────────────────────────────
def write_post(content: str, data: dict):
    # 标题：优先用 A 股涨跌幅最大的指数，其次用全球指数
    all_indices = {**data.get("a_indices", {}), **data.get("global_indices", {})}
    if all_indices:
        top = max(all_indices.items(), key=lambda x: abs(x[1]["change"]))
        title = f"{TODAY} 全球财经日报：{top[0]} {top[1]['change']:+.2f}%，市场深度解析"
    else:
        title = f"{TODAY} 全球财经日报：A股·美股·大宗商品深度解析"

    # 摘要：取各板块代表数据
    sp500  = data.get("global_indices", {}).get("标普500", {})
    gold   = data.get("commodities", {}).get("黄金($/oz)", {})
    desc_parts = []
    if sp500:
        desc_parts.append(f"标普500 {sp500['change']:+.2f}%")
    if gold:
        desc_parts.append(f"黄金 ${gold['price']:.0f}")
    desc_extra = "，".join(desc_parts)
    description = f"{TODAY} 全球财经日报，涵盖A股、港股、美股、大宗商品、加密货币及汇率深度分析。{desc_extra}"

    front_matter = textwrap.dedent(f"""
        ---
        title: "{title}"
        date: {NOW}
        tags:
          - A股
          - 美股
          - 全球市场
          - 大宗商品
          - 财经日报
          - AI生成
        categories:
          - 金融资讯
        description: "{description}"
        ---
    """).strip()

    filepath = POSTS_DIR / f"{TODAY}-daily-report.md"
    filepath.write_text(f"{front_matter}\n\n{content}\n", encoding="utf-8")
    print(f"✅ 文章已生成：{filepath}")


# ── 主流程 ─────────────────────────────────────────────────────────────────────
def main():
    print(f"[{NOW}] 开始生成全球财经日报...")

    print("→ 拉取金融数据...")
    data = fetch_market_data()
    print(f"  A股指数:   {list(data.get('a_indices', {}).keys())}")
    print(f"  全球指数:  {list(data.get('global_indices', {}).keys())}")
    print(f"  大宗商品:  {list(data.get('commodities', {}).keys())}")
    print(f"  加密货币:  {list(data.get('crypto', {}).keys())}")
    print(f"  汇率:      {list(data.get('forex', {}).keys())}")

    print("→ 调用 LLM 生成内容...")
    prompt  = build_prompt(data)
    content = call_llm(prompt)
    print(f"  生成字数: {len(content)}")

    print("→ 写入 Markdown 文件...")
    write_post(content, data)

    print("完成 ✓")


if __name__ == "__main__":
    main()
