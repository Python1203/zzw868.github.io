"""
LSTM 价格预测模型训练脚本
- 数据源：Binance REST API K线（无需 API Key，公开接口）
- 模型：双层 LSTM → Dense，预测下一根 K 线收盘价
- 输出：models/crypto_lstm_model.h5 + models/scaler.gz

运行：
    source venv312/bin/activate
    python train_lstm.py [--symbol BTCUSDT] [--interval 1h] [--limit 2000]
"""

import argparse
import os
import joblib
import requests
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

WINDOW_SIZE = 60
MODEL_DIR   = "models"


def fetch_klines(symbol: str, interval: str, limit: int) -> np.ndarray:
    """从 Binance 公开 REST 接口拉取 K 线收盘价，无需 API Key"""
    url = "https://api.binance.com/api/v3/klines"
    prices = []
    # 分批拉取（单次最多 1000 条）
    fetched = 0
    end_time = None
    while fetched < limit:
        batch = min(1000, limit - fetched)
        params = {"symbol": symbol, "interval": interval, "limit": batch}
        if end_time:
            params["endTime"] = end_time
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        # K线格式: [open_time, open, high, low, close, volume, ...]
        batch_prices = [float(k[4]) for k in data]
        prices = batch_prices + prices
        end_time = data[0][0] - 1   # 向前翻页
        fetched += len(data)
        print(f"  已拉取 {fetched} 条 {symbol} {interval} K线")
        if len(data) < batch:
            break

    arr = np.array(prices[-limit:], dtype=float)
    print(f"✅ 共获取 {len(arr)} 条收盘价，最新价: {arr[-1]:.2f}")
    return arr


def build_dataset(prices: np.ndarray, scaler: MinMaxScaler):
    scaled = scaler.fit_transform(prices.reshape(-1, 1)).flatten()
    X, y = [], []
    for i in range(WINDOW_SIZE, len(scaled)):
        X.append(scaled[i - WINDOW_SIZE:i])
        y.append(scaled[i])
    X = np.array(X).reshape(-1, WINDOW_SIZE, 1)
    y = np.array(y)
    # 80/20 时序分割（不随机打乱，保持时间顺序）
    split = int(len(X) * 0.8)
    return X[:split], X[split:], y[:split], y[split:]


def build_model() -> Sequential:
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=(WINDOW_SIZE, 1)),
        Dropout(0.2),
        LSTM(64, return_sequences=False),
        Dropout(0.2),
        Dense(32, activation="relu"),
        Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    model.summary()
    return model


def train(symbol: str, interval: str, limit: int):
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path  = os.path.join(MODEL_DIR, "crypto_lstm_model.keras")
    scaler_path = os.path.join(MODEL_DIR, "scaler.gz")

    print(f"\n📥 拉取 {symbol} {interval} K线数据...")
    prices = fetch_klines(symbol, interval, limit)

    scaler = MinMaxScaler(feature_range=(0, 1))
    X_train, X_test, y_train, y_test = build_dataset(prices, scaler)
    print(f"📊 训练集: {len(X_train)} 条，测试集: {len(X_test)} 条")

    model = build_model()

    callbacks = [
        EarlyStopping(patience=10, restore_best_weights=True, verbose=1),
        ModelCheckpoint(model_path, save_best_only=True, verbose=0),
    ]

    print("\n🚀 开始训练...")
    model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=100,
        batch_size=32,
        callbacks=callbacks,
        verbose=1,
    )

    # 评估
    loss, mae = model.evaluate(X_test, y_test, verbose=0)
    # 反归一化 MAE → 实际价格误差
    mae_price = float(scaler.inverse_transform([[mae]])[0][0] -
                      scaler.inverse_transform([[0.0]])[0][0])
    print(f"\n✅ 测试集 MAE: {mae_price:.2f} USDT")

    joblib.dump(scaler, scaler_path)
    print(f"💾 模型已保存: {model_path}")
    print(f"💾 Scaler 已保存: {scaler_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol",   default="BTCUSDT")
    parser.add_argument("--interval", default="1h",
                        choices=["1m","5m","15m","1h","4h","1d"])
    parser.add_argument("--limit",    default=2000, type=int)
    args = parser.parse_args()
    train(args.symbol, args.interval, args.limit)
