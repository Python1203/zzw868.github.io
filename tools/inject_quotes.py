#!/usr/bin/env python3
"""
scripts/inject_quotes.py

功能：拉取实时行情点位，以 Markdown 表格形式注入博文正文。
用法：
  # 注入今日文章
  python scripts/inject_quotes.py

  # 注入指定文件
  python scripts/inject_quotes.py source/_posts/2026-03-17-financial-report.md

注入位置：文章 Front-matter 结束后的第一行（<!-- QUOTES -->占位符）。
若文章中无占位符，则自动插入到正文第一段之前。
"""

import os
import sys
import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env", override=False)
except ImportError:
    pass


# ── 行情标的配置 ───────────────────────────────────────────────────────────────
QUOTES_CONFIG = [
    # (显示名称,          Ticker,            类别,      颜色标记阈值)
    ("标普 500",          "^GSPC",           "美股",    2.0),
    ("纳斯达克 100",      "^IXIC",           "美股",    2.0),
    ("恒生指数",          "^HSI",            "港股",    2.0),
    ("上证指数",          "000001.SS",       "A股",     2.0),
    ("WTI 原油",          "CL=F",            "大宗",    3.0),
    ("黄金",              "GC=F",            "大宗",    1.5),
    ("BTC/USDT",          "BTC-USD",         "加密",    5.0),
    ("离岸人民币",        "USDCNH=X",        "外汇",    0.5),
]

PLACEHOLDER = "<!-- QUOTES -->"


# ── 1. 拉取实时行情 ────────────────────────────────────────────────────────────
def fetch_quotes() -> list[dict]:
    results = []
    for name, ticker, category, threshold in QUOTES_CONFIG:
        try:
            info       = yf.Ticker(ticker).fast_info
            price      = float(info.last_price)
            prev       = float(info.previous_close)
            change_pct = (price - prev) / prev * 100 if prev else 0.0

            # 涨跌幅标记
            if change_pct >= threshold:
                badge = "🚀"
            elif change_pct <= -threshold:
                badge = "🔻"
            else:
                badge = "➡️"

            results.append({
                "name":       name,
                "category":   category,
                "price":      price,
                "change_pct": change_pct,
                "badge":      badge,
            })
        except Exception as e:
            print(f"[WARN] {name} ({ticker}) 获取失败: {e}")
            results.append({
                "name":       name,
                "category":   category,
                "price":      None,
                "change_pct": None,
                "badge":      "❓",
            })
    return results


# ── 2. 生成 Markdown 行情表格 ──────────────────────────────────────────────────
def build_quotes_block(quotes: list[dict]) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"> 📊 **实时行情** · 数据更新于 {now} BJT · 来源：Yahoo Finance",
        ">",
        "> | 资产 | 类别 | 最新价 | 涨跌幅 | 情绪 |",
        "> |------|------|-------:|-------:|:----:|",
    ]
    for q in quotes:
        if q["price"] is not None:
            price_str  = f"{q['price']:,.2f}"
            change_str = f"{q['change_pct']:+.2f}%"
        else:
            price_str  = "N/A"
            change_str = "N/A"
        lines.append(
            f"> | {q['name']} | {q['category']} "
            f"| {price_str} | {change_str} | {q['badge']} |"
        )
    lines.append(">")
    lines.append("> *以上数据仅供参考，不构成投资建议。*")
    return "\n".join(lines)


# ── 3. 注入到博文 ──────────────────────────────────────────────────────────────
def inject_into_post(filepath: Path, block: str) -> bool:
    content = filepath.read_text(encoding="utf-8")

    # 已有占位符：直接替换
    if PLACEHOLDER in content:
        new_content = content.replace(PLACEHOLDER, block, 1)
        filepath.write_text(new_content, encoding="utf-8")
        print(f"✅ 已替换占位符注入行情：{filepath.name}")
        return True

    # 无占位符：插入到 Front-matter 结束后第一个空行之后
    lines  = content.split("\n")
    fm_end = None
    in_fm  = False
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_fm = True
            continue
        if in_fm and line.strip() == "---":
            fm_end = i
            break

    if fm_end is not None:
        # 在 Front-matter 结束行后插入，空一行再插入表格
        insert_at = fm_end + 1
        # 跳过紧跟的空行
        while insert_at < len(lines) and lines[insert_at].strip() == "":
            insert_at += 1
        lines.insert(insert_at, "")
        lines.insert(insert_at, block)
        filepath.write_text("\n".join(lines), encoding="utf-8")
        print(f"✅ 已注入行情表格到正文开头：{filepath.name}")
        return True

    print(f"[WARN] 未找到 Front-matter，跳过：{filepath.name}")
    return False


# ── 4. 定位今日文章 ────────────────────────────────────────────────────────────
def find_today_post() -> Path | None:
    posts_dir = Path(__file__).parent.parent / "source" / "_posts"
    today     = datetime.datetime.now().strftime("%Y-%m-%d")
    # 匹配今日所有文章，优先选 financial-report
    candidates = sorted(posts_dir.glob(f"{today}-*.md"))
    for p in candidates:
        if "financial-report" in p.name:
            return p
    return candidates[0] if candidates else None


# ── 主流程 ─────────────────────────────────────────────────────────────────────
def main():
    # 支持命令行指定文件
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = find_today_post()

    if not target or not target.exists():
        print("❌ 未找到目标文章，请先运行 main.py 生成博文，或手动指定路径。")
        sys.exit(1)

    print(f"→ 目标文章：{target}")
    print("→ 拉取实时行情...")
    quotes = fetch_quotes()

    available = [q for q in quotes if q["price"] is not None]
    print(f"  成功获取 {len(available)}/{len(quotes)} 个标的")

    print("→ 生成行情表格...")
    block = build_quotes_block(quotes)

    print("→ 注入博文...")
    inject_into_post(target, block)
    print("完成 ✓")


if __name__ == "__main__":
    main()
