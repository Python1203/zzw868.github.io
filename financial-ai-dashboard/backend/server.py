"""
金融AI实时行情后端
- 上游①：Binance / Huobi / OKX 三大公开免费 WebSocket（无需 API Key）
- 上游②：iTick WebSocket 外汇 + 股票/期货行情
- AI①：RSI + MACD + Bollinger Bands + 动量评分，每 ITER_EVERY 条迭代
- AI②：LSTM 深度学习价格预测（需先运行 train_lstm.py 生成模型）
- 交易：Binance 现货下单（TRADE_ENABLED=true 时启用，默认关闭）
- 密钥：全部从 .env 读取，代码中无明文
- 下游：广播 AI 信号 + 行情快照给所有前端客户端（ws://localhost:8080）
"""

import asyncio
import json
import logging
import os
import ssl
import threading
import zlib
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

import certifi
import numpy as np
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

import websocket          # websocket-client（同步，用于 iTick header 认证）
import websockets         # websockets（异步，用于三大交易所 + 前端服务）
from websockets.asyncio.server import serve

# macOS Python 需要显式指定 certifi CA bundle，否则 SSL 握手失败
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ── 配置 ──────────────────────────────────────────────────────────────────────
BACKEND_PORT = 8080
HISTORY_LEN  = 200
ITER_EVERY   = 10
RECONNECT_S  = 5

# ── 从 .env 读取密钥 ──────────────────────────────────────────────────────────
BINANCE_API_KEY    = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
TRADE_SYMBOL       = os.getenv("TRADE_SYMBOL", "BTCUSDT")
TRADE_QUANTITY     = float(os.getenv("TRADE_QUANTITY", "0.001"))
TRADE_THRESHOLD    = float(os.getenv("TRADE_THRESHOLD", "0.003"))
TRADE_ENABLED      = os.getenv("TRADE_ENABLED", "false").lower() == "true"
LSTM_MODEL_PATH    = os.getenv("LSTM_MODEL_PATH", "models/crypto_lstm_model.keras")
LSTM_SCALER_PATH   = os.getenv("LSTM_SCALER_PATH", "models/scaler.gz")

# iTick 外汇（付费账户，header 认证）
ITICK_TOKEN      = os.getenv("ITICK_TOKEN", "")
ITICK_FOREX_URL  = "wss://api.itick.org/forex"
FOREX_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
    "AUDUSD", "USDCAD", "NZDUSD", "EURGBP",
]

# iTick 股票/期货（免费测试节点，subscribe 消息认证）
ITICK_STOCK_URL  = "wss://api-free.itick.org/stock"
# 格式：期货用 "XAUUSD"，美股用 "AAPL$US"，港股用 "00700$HK"
STOCK_SYMBOLS    = "XAUUSD,XAGUSD,AAPL$US,TSLA$US,00700$HK,600519$CN"

# Binance 订阅的交易对（小写）
BINANCE_SYMBOLS = [
    "btcusdt", "ethusdt", "solusdt", "bnbusdt",
    "xrpusdt", "dogeusdt", "adausdt", "avaxusdt",
]

# Huobi 订阅的交易对（小写）
HUOBI_SYMBOLS = [
    "btcusdt", "ethusdt", "solusdt", "bnbusdt",
    "xrpusdt", "dogeusdt", "adausdt", "avaxusdt",
]

# OKX 订阅的 instId（大写，现货）
OKX_INST_IDS = [
    "BTC-USDT", "ETH-USDT", "SOL-USDT", "BNB-USDT",
    "XRP-USDT", "DOGE-USDT", "ADA-USDT", "AVAX-USDT",
]

# ── 状态 ──────────────────────────────────────────────────────────────────────
clients: set = set()
price_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=HISTORY_LEN))
tick_counter:  dict[str, int]   = defaultdict(int)
latest_signals: dict[str, dict] = {}


# ── AI 算法层 ─────────────────────────────────────────────────────────────────

def _ema(arr: np.ndarray, period: int) -> np.ndarray:
    k, out = 2 / (period + 1), np.empty_like(arr)
    out[0] = arr[0]
    for i in range(1, len(arr)):
        out[i] = arr[i] * k + out[i - 1] * (1 - k)
    return out


def compute_rsi(prices: np.ndarray, period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0
    deltas = np.diff(prices[-(period + 1):])
    gains  = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_loss = losses.mean()
    if avg_loss == 0:
        return 100.0
    return round(100 - 100 / (1 + gains.mean() / avg_loss), 2)


def compute_macd(prices: np.ndarray) -> dict:
    if len(prices) < 26:
        return {"macd": 0.0, "signal": 0.0, "hist": 0.0}
    macd_line = _ema(prices, 12) - _ema(prices, 26)
    signal    = _ema(macd_line, 9)
    return {
        "macd":   round(float(macd_line[-1]), 4),
        "signal": round(float(signal[-1]), 4),
        "hist":   round(float((macd_line - signal)[-1]), 4),
    }


def compute_bollinger(prices: np.ndarray, period: int = 20) -> dict:
    if len(prices) < period:
        return {"upper": 0.0, "mid": 0.0, "lower": 0.0, "pct_b": 0.5}
    w   = prices[-period:]
    mid = w.mean(); std = w.std()
    upper, lower = mid + 2 * std, mid - 2 * std
    pct_b = float((prices[-1] - lower) / (upper - lower)) if upper != lower else 0.5
    return {"upper": round(float(upper), 4), "mid": round(float(mid), 4),
            "lower": round(float(lower), 4), "pct_b": round(pct_b, 4)}


def run_ai_iteration(key: str, prices: np.ndarray) -> dict:
    rsi  = compute_rsi(prices)
    macd = compute_macd(prices)
    boll = compute_bollinger(prices)
    score, reasons = 0, []

    if rsi < 30:   score += 1; reasons.append("RSI超卖")
    elif rsi > 70: score -= 1; reasons.append("RSI超买")

    if macd["hist"] > 0:   score += 1; reasons.append("MACD金叉")
    elif macd["hist"] < 0: score -= 1; reasons.append("MACD死叉")

    if boll["pct_b"] < 0.05:   score += 1; reasons.append("触及下轨")
    elif boll["pct_b"] > 0.95: score -= 1; reasons.append("触及上轨")

    if len(prices) >= 5:
        m = float(prices[-1] - prices[-5])
        if m > 0:   score += 1; reasons.append("短期上涨动量")
        elif m < 0: score -= 1; reasons.append("短期下跌动量")

    labels = {4:"强烈看涨", 3:"强烈看涨", 2:"看涨", 1:"温和看涨",
              0:"中性", -1:"温和看跌", -2:"看跌", -3:"强烈看跌", -4:"强烈看跌"}
    return {
        "key": key, "score": score,
        "label": labels.get(score, "中性"),
        "rise_prob": round(min(max((score + 4) / 8, 0.05), 0.95), 3),
        "rsi": rsi, "macd": macd, "bollinger": boll, "reasons": reasons,
        "iterated_at": datetime.now(timezone.utc).isoformat(),
    }


# ── LSTM 推理层 ───────────────────────────────────────────────────────────────

_lstm_model  = None
_lstm_scaler = None
WINDOW_SIZE  = 60


def _load_lstm():
    global _lstm_model, _lstm_scaler
    if _lstm_model is not None:
        return True
    model_path  = Path(__file__).parent / LSTM_MODEL_PATH
    scaler_path = Path(__file__).parent / LSTM_SCALER_PATH
    if not model_path.exists() or not scaler_path.exists():
        return False
    try:
        import joblib
        from tensorflow.keras.models import load_model
        _lstm_model  = load_model(str(model_path))
        _lstm_scaler = joblib.load(str(scaler_path))
        log.info("✅ LSTM 模型已加载: %s", model_path)
        return True
    except Exception as e:
        log.warning("❌ LSTM 加载失败: %s", e)
        return False


def lstm_predict(prices: np.ndarray) -> dict | None:
    if len(prices) < WINDOW_SIZE or not _load_lstm():
        return None
    try:
        inp = prices[-WINDOW_SIZE:].reshape(-1, 1)
        scaled = _lstm_scaler.transform(inp).reshape(1, WINDOW_SIZE, 1)
        pred_scaled = _lstm_model.predict(scaled, verbose=0)
        predicted = float(_lstm_scaler.inverse_transform(pred_scaled)[0][0])
        current   = float(prices[-1])
        change    = (predicted - current) / current
        if change > TRADE_THRESHOLD:
            signal = "BUY"
        elif change < -TRADE_THRESHOLD:
            signal = "SELL"
        else:
            signal = "HOLD"
        return {
            "predicted_price": round(predicted, 4),
            "current_price":   round(current, 4),
            "change_pct":      round(change * 100, 3),
            "signal":          signal,
            "rise_prob":       round(min(max(change / (TRADE_THRESHOLD * 2) + 0.5, 0.05), 0.95), 3),
        }
    except Exception as e:
        log.debug("LSTM 推理异常: %s", e)
        return None


# ── Binance 交易执行层 ────────────────────────────────────────────────────────

_binance_client = None


def _get_binance_client():
    global _binance_client
    if _binance_client:
        return _binance_client
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        return None
    try:
        from binance.client import Client
        _binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        log.info("✅ Binance 交易客户端已初始化")
        return _binance_client
    except Exception as e:
        log.warning("❌ Binance 客户端初始化失败: %s", e)
        return None


async def execute_trade(signal: str, symbol: str, predicted_price: float):
    if not TRADE_ENABLED:
        log.info("[交易模拟] %s %s @ 预测价 %.4f（TRADE_ENABLED=false）",
                 signal, symbol, predicted_price)
        await broadcast({"type": "trade_signal", "data": {
            "signal": signal, "symbol": symbol,
            "predicted_price": predicted_price, "dry_run": True,
        }})
        return
    client = _get_binance_client()
    if not client:
        log.warning("交易失败：Binance 客户端未初始化（检查 .env）")
        return
    try:
        from binance.client import Client as BClient
        order = client.create_order(
            symbol=symbol, side=signal,
            type=BClient.ORDER_TYPE_MARKET, quantity=TRADE_QUANTITY,
        )
        fill_price = order["fills"][0]["price"] if order.get("fills") else "N/A"
        log.info("🚀 [交易执行] %s %s 成功！成交价: %s", signal, symbol, fill_price)
        await broadcast({"type": "trade_signal", "data": {
            "signal": signal, "symbol": symbol,
            "fill_price": fill_price, "dry_run": False,
        }})
    except Exception as e:
        log.error("❌ 交易失败: %s", e)


# ── 公共：处理一条标准化行情 ──────────────────────────────────────────────────

async def on_tick(source: str, symbol: str, price: float, extra: dict, region: str = "crypto"):
    """所有交易所行情统一入口，region 区分资产类别"""
    key = f"{region}:{symbol.upper()}"
    price_history[key].append(price)
    tick_counter[key] += 1

    payload = {"s": symbol.upper(), "p": price, "r": region,
               "src": source, **extra}
    await broadcast({"type": "quote", "data": payload})

    if tick_counter[key] % ITER_EVERY == 0:
        arr = np.array(price_history[key], dtype=float)
        sig = run_ai_iteration(key, arr)
        latest_signals[key] = sig

        # LSTM 推理（模型存在时附加预测结果）
        lstm = lstm_predict(arr)
        if lstm:
            sig["lstm"] = lstm
            # 仅对 TRADE_SYMBOL 触发交易逻辑
            if lstm["signal"] != "HOLD" and symbol.upper() == TRADE_SYMBOL:
                await execute_trade(lstm["signal"], TRADE_SYMBOL, lstm["predicted_price"])

        await broadcast({"type": "ai_signal", "data": sig})
        log.info("[%s] AI迭代 %s → %s (score=%d)", source, key, sig["label"], sig["score"])


# ── Binance Feed ──────────────────────────────────────────────────────────────

async def binance_feed():
    """
    订阅 Binance 组合流：每个 symbol 的 miniTicker
    wss://stream.binance.com:9443/stream?streams=btcusdt@miniTicker/ethusdt@miniTicker/...
    消息格式: {"stream":"btcusdt@miniTicker","data":{"s":"BTCUSDT","c":"65000.00",...}}
    单连接有效期 24h，到期前主动重连。
    """
    streams = "/".join(f"{s}@miniTicker" for s in BINANCE_SYMBOLS)
    url = f"wss://stream.binance.com:9443/stream?streams={streams}"
    while True:
        try:
            async with websockets.connect(url, ssl=SSL_CTX, ping_interval=20, open_timeout=10) as ws:
                log.info("[Binance] 已连接，订阅 %d 个交易对", len(BINANCE_SYMBOLS))
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                        d   = msg.get("data", {})
                        if d.get("e") == "24hrMiniTicker":
                            await on_tick("Binance", d["s"], float(d["c"]), {
                                "h": float(d["h"]), "l": float(d["l"]),
                                "v": float(d["v"]), "ch": float(d["c"]) - float(d["o"]),
                            })
                    except Exception:
                        continue
        except Exception as e:
            log.warning("[Binance] 断开: %s，%ds 后重连…", e, RECONNECT_S)
            await asyncio.sleep(RECONNECT_S)


# ── Huobi Feed ────────────────────────────────────────────────────────────────

async def huobi_feed():
    """
    Huobi 推送 GZIP 压缩二进制，需用 zlib.decompress 解压。
    心跳：服务端发 {"ping": ts}，客户端必须回 {"pong": ts}，否则断连。
    订阅格式: {"sub": "market.btcusdt.ticker", "id": "btcusdt"}
    """
    url = "wss://api.huobi.pro/ws"
    while True:
        try:
            async with websockets.connect(url, ssl=SSL_CTX, ping_interval=None, open_timeout=10) as ws:
                log.info("[Huobi] 已连接，订阅 %d 个交易对", len(HUOBI_SYMBOLS))
                for sym in HUOBI_SYMBOLS:
                    await ws.send(json.dumps({"sub": f"market.{sym}.ticker", "id": sym}))

                async for raw in ws:
                    # Huobi 消息为 GZIP 二进制
                    try:
                        text = zlib.decompress(raw, 16 + zlib.MAX_WBITS).decode()
                        msg  = json.loads(text)
                    except Exception:
                        continue

                    # 心跳响应（必须，否则 Huobi 会断连）
                    if "ping" in msg:
                        await ws.send(json.dumps({"pong": msg["ping"]}))
                        continue

                    tick = msg.get("tick")
                    ch   = msg.get("ch", "")          # e.g. "market.btcusdt.ticker"
                    if tick and ".ticker" in ch:
                        sym = ch.split(".")[1].upper() # "BTCUSDT"
                        await on_tick("Huobi", sym, float(tick["close"]), {
                            "h": float(tick["high"]), "l": float(tick["low"]),
                            "v": float(tick["vol"]),
                            "ch": float(tick["close"]) - float(tick["open"]),
                        })
        except Exception as e:
            log.warning("[Huobi] 断开: %s，%ds 后重连…", e, RECONNECT_S)
            await asyncio.sleep(RECONNECT_S)


# ── OKX Feed ──────────────────────────────────────────────────────────────────

async def okx_feed():
    """
    OKX 支持批量订阅，单次 subscribe 传入 args 数组。
    消息格式: {"arg":{"channel":"tickers","instId":"BTC-USDT"},"data":[{...}]}
    服务端每 30s 发一次 {"event":"ping"}，需回 {"op":"pong"}。
    """
    url = "wss://ws.okx.com:8443/ws/v5/public"
    args = [{"channel": "tickers", "instId": inst} for inst in OKX_INST_IDS]
    while True:
        try:
            async with websockets.connect(url, ssl=SSL_CTX, ping_interval=None, open_timeout=10) as ws:
                log.info("[OKX] 已连接，订阅 %d 个交易对", len(OKX_INST_IDS))
                await ws.send(json.dumps({"op": "subscribe", "args": args}))

                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                    except Exception:
                        continue

                    # OKX 心跳
                    if msg.get("event") == "ping" or raw == "ping":
                        await ws.send(json.dumps({"op": "pong"}))
                        continue

                    data_list = msg.get("data")
                    if not data_list:
                        continue
                    for d in data_list:
                        if not d.get("last"):
                            continue
                        inst = d.get("instId", "").replace("-", "")  # BTC-USDT → BTCUSDT
                        await on_tick("OKX", inst, float(d["last"]), {
                            "h": float(d.get("high24h", 0)),
                            "l": float(d.get("low24h", 0)),
                            "v": float(d.get("vol24h", 0)),
                            "ch": float(d["last"]) - float(d.get("open24h", d["last"])),
                        })
        except Exception as e:
            log.warning("[OKX] 断开: %s，%ds 后重连…", e, RECONNECT_S)
            await asyncio.sleep(RECONNECT_S)


# ── iTick 外汇 Feed（同步 websocket-client，线程桥接进 asyncio）────────────────

def _itick_thread(loop: asyncio.AbstractEventLoop):
    """
    iTick 使用 header 认证，websockets 异步库不支持自定义 header，
    故用同步 websocket-client 在独立线程运行，通过 call_soon_threadsafe 桥接回主循环。
    """
    def on_open(ws):
        log.info("[iTick] 已连接，订阅 %d 个外汇对", len(FOREX_SYMBOLS))
        # iTick 需先发 auth，认证成功后再订阅
        ws.send(json.dumps({"cmd": "auth", "args": [ITICK_TOKEN]}))

    def on_message(ws, msg):
        try:
            data = json.loads(msg)
            # 认证成功回调 → 批量订阅
            if data.get("cmd") == "auth" or data.get("type") == "auth":
                log.info("[iTick] 认证成功，开始订阅外汇对")
                for sym in FOREX_SYMBOLS:
                    ws.send(json.dumps({"cmd": "subscribe", "args": [f"forex.{sym}.quote"]}))
                return
            # iTick 行情格式: {"s":"EURUSD","p":1.0823,"h":...,"l":...,"ch":...,"chp":...}
            d = data.get("data") or data
            if not d or not d.get("s") or d.get("p") is None:
                return
            sym   = d["s"]
            price = float(d["p"])
            extra = {
                "h":   float(d.get("h", price)),
                "l":   float(d.get("l", price)),
                "ch":  float(d.get("ch", 0)),
                "chp": float(d.get("chp", 0)),
            }
            # 桥接：将协程调度到 asyncio 主循环
            asyncio.run_coroutine_threadsafe(
                on_tick("iTick", sym, price, extra, region="forex"),
                loop
            )
        except Exception as e:
            log.debug("[iTick] 消息解析异常: %s", e)

    def on_error(ws, err):
        log.warning("[iTick] 错误: %s", err)

    def on_close(ws, code, msg):
        log.warning("[iTick] 断开 (code=%s)，%ds 后重连…", code, RECONNECT_S)

    while True:
        try:
            ws = websocket.WebSocketApp(
                ITICK_FOREX_URL,
                header={"token": ITICK_TOKEN},
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )
            ws.run_forever(
                reconnect=RECONNECT_S,
                sslopt={"ca_certs": certifi.where()},
            )
        except Exception as e:
            log.warning("[iTick] 线程异常: %s，%ds 后重启…", e, RECONNECT_S)
            import time; time.sleep(RECONNECT_S)


async def itick_forex_feed(loop: asyncio.AbstractEventLoop):
    """在 daemon 线程中启动 iTick 同步客户端"""
    t = threading.Thread(target=_itick_thread, args=(loop,), daemon=True)
    t.start()
    log.info("[iTick] 外汇线程已启动")
    while True:
        await asyncio.sleep(60)


# ── iTick 股票/期货 Feed（免费节点，subscribe 消息认证）────────────────────────

def _itick_stock_thread(loop: asyncio.AbstractEventLoop):
    """
    免费节点 wss://api-free.itick.org/stock
    认证方式：直接发 subscribe 消息，无需 header token。
    消息格式: {"ac":"subscribe","params":"XAUUSD,AAPL$US","types":"quote"}
    行情推送: {"s":"XAUUSD","p":1920.5,"h":...,"l":...,"ch":...}
    """
    def on_open(ws):
        log.info("[iTick-Stock] 已连接，订阅: %s", STOCK_SYMBOLS)
        ws.send(json.dumps({"ac": "subscribe", "params": STOCK_SYMBOLS, "types": "quote"}))

    def on_message(ws, msg):
        try:
            data = json.loads(msg)
            d = data.get("data") or data
            if not d or not d.get("s") or d.get("p") is None:
                return
            sym   = str(d["s"]).replace("$", "_")   # AAPL$US → AAPL_US
            price = float(d["p"])
            # 判断 region：期货(无$)→ futures，否则按后缀
            raw_s = str(d["s"])
            if "$" not in raw_s:
                region = "futures"
            else:
                suffix = raw_s.split("$")[-1].upper()
                region = {"US": "us", "HK": "hk", "CN": "cn"}.get(suffix, "stock")
            extra = {
                "h":  float(d.get("h", price)),
                "l":  float(d.get("l", price)),
                "ch": float(d.get("ch", 0)),
            }
            asyncio.run_coroutine_threadsafe(
                on_tick("iTick-Stock", sym, price, extra, region=region), loop
            )
        except Exception as e:
            log.debug("[iTick-Stock] 消息解析异常: %s", e)

    def on_error(ws, err):
        log.warning("[iTick-Stock] 错误: %s", err)

    def on_close(ws, code, msg):
        log.warning("[iTick-Stock] 断开 (code=%s)，%ds 后重连…", code, RECONNECT_S)

    while True:
        try:
            ws = websocket.WebSocketApp(
                ITICK_STOCK_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )
            ws.run_forever(reconnect=RECONNECT_S, sslopt={"ca_certs": certifi.where()})
        except Exception as e:
            log.warning("[iTick-Stock] 线程异常: %s，%ds 后重启…", e, RECONNECT_S)
            import time; time.sleep(RECONNECT_S)


async def itick_stock_feed(loop: asyncio.AbstractEventLoop):
    t = threading.Thread(target=_itick_stock_thread, args=(loop,), daemon=True)
    t.start()
    log.info("[iTick-Stock] 股票/期货线程已启动")
    while True:
        await asyncio.sleep(60)


# ── 广播 ──────────────────────────────────────────────────────────────────────

async def broadcast(msg: dict):
    if not clients:
        return
    data = json.dumps(msg)
    await asyncio.gather(*[c.send(data) for c in list(clients)], return_exceptions=True)


# ── 前端客户端处理 ─────────────────────────────────────────────────────────────

async def client_handler(ws):
    clients.add(ws)
    log.info("前端连接，当前 %d 个客户端", len(clients))
    try:
        # ① 历史价格快照：每个 key 最近 HISTORY_LEN 条价格序列
        if price_history:
            history_payload = {
                key: list(prices)
                for key, prices in price_history.items()
                if prices
            }
            await ws.send(json.dumps({"type": "history_snapshot", "data": history_payload}))

        # ② AI 信号快照：所有 key 的最新迭代结果
        if latest_signals:
            await ws.send(json.dumps({"type": "ai_snapshot", "data": latest_signals}))

        log.info("快照已推送：%d 个历史序列，%d 个AI信号",
                 len(price_history), len(latest_signals))
        await ws.wait_closed()
    finally:
        clients.discard(ws)
        log.info("前端断开，当前 %d 个客户端", len(clients))


# ── 入口 ──────────────────────────────────────────────────────────────────────

async def main():
    log.info("🚀 金融AI后端启动，端口 %d", BACKEND_PORT)
    loop = asyncio.get_running_loop()
    async with serve(client_handler, "localhost", BACKEND_PORT):
        log.info("✅ 前端 WebSocket 就绪: ws://localhost:%d", BACKEND_PORT)
        # 四路行情并发：三大加密交易所 + iTick 外汇
        await asyncio.gather(
            binance_feed(),
            huobi_feed(),
            okx_feed(),
            itick_forex_feed(loop),
            itick_stock_feed(loop),
        )


if __name__ == "__main__":
    asyncio.run(main())
