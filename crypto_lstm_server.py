"""
crypto_lstm_server.py
─────────────────────
启动: python crypto_lstm_server.py
依赖: pip install websockets tensorflow scikit-learn numpy joblib aiohttp
"""
import asyncio, json, logging, os
import numpy as np
import websockets
from websockets.server import serve

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

MODEL_PATH  = "crypto_lstm_model.h5"
SCALER_PATH = "scaler.gz"
SEQ_LEN     = 60
PRED_STEPS  = 6          # 预测未来 1~6 步
PORT        = 8765

# ── 懒加载模型（首次连接时加载，避免启动慢）────────────────────────────────────
_model  = None
_scaler = None

def load_artifacts():
    global _model, _scaler
    if _model is not None:
        return True
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        log.warning("模型文件不存在，请先运行 train_lstm.py")
        return False
    from tensorflow.keras.models import load_model
    import joblib
    _model  = load_model(MODEL_PATH)
    _scaler = joblib.load(SCALER_PATH)
    log.info("模型加载完成")
    return True

# ── 多步预测（自回归） ────────────────────────────────────────────────────────
def predict_steps(window: list[float]) -> list[float]:
    arr = np.array(window, dtype=np.float32).reshape(-1, 1)
    scaled = _scaler.transform(arr)
    buf = list(scaled.flatten())
    preds = []
    for _ in range(PRED_STEPS):
        x = np.array(buf[-SEQ_LEN:]).reshape(1, SEQ_LEN, 1)
        y = _model.predict(x, verbose=0)[0][0]
        buf.append(float(y))
        preds.append(float(_scaler.inverse_transform([[y]])[0][0]))
    return preds

# ── 每个客户端连接的状态 ──────────────────────────────────────────────────────
class ClientSession:
    def __init__(self):
        self.window: list[float] = []

    def push(self, price: float) -> dict | None:
        self.window.append(price)
        if len(self.window) > SEQ_LEN * 2:
            self.window.pop(0)
        if len(self.window) < SEQ_LEN:
            return {"type": "WARMING_UP", "need": SEQ_LEN - len(self.window)}
        if not load_artifacts():
            return {"type": "ERROR", "msg": "模型未加载"}
        try:
            preds = predict_steps(self.window[-SEQ_LEN:])
            hours = [1, 2, 3, 4, 5, 6]
            return {
                "type": "AI_PREDICTION",
                "current": price,
                "trend": "UP" if preds[0] > price else "DOWN",
                "predictions": [{"h": h, "price": round(p, 4)} for h, p in zip(hours, preds)],
                "confidence": round(min(len(self.window) / (SEQ_LEN * 2), 1.0), 2)
            }
        except Exception as e:
            log.error("预测失败: %s", e)
            return {"type": "ERROR", "msg": str(e)}

# ── WebSocket 处理器 ──────────────────────────────────────────────────────────
async def handler(websocket):
    session = ClientSession()
    remote = websocket.remote_address
    log.info("客户端连接: %s", remote)
    try:
        async for raw in websocket:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"type": "ERROR", "msg": "invalid json"}))
                continue

            if "price" not in data:
                await websocket.send(json.dumps({"type": "ERROR", "msg": "缺少 price 字段"}))
                continue

            result = session.push(float(data["price"]))
            if result:
                await websocket.send(json.dumps(result))
    except websockets.exceptions.ConnectionClosedOK:
        pass
    except Exception as e:
        log.error("连接异常 %s: %s", remote, e)
    finally:
        log.info("客户端断开: %s", remote)

# ── 启动 ──────────────────────────────────────────────────────────────────────
async def main():
    log.info("LSTM WS 服务启动 ws://localhost:%d", PORT)
    async with serve(handler, "localhost", PORT, ping_interval=20, ping_timeout=10):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
