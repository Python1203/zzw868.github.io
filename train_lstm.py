"""
train_lstm.py
─────────────
用法: python train_lstm.py [--symbol BTCUSDT] [--epochs 20]
输出: crypto_lstm_model.h5  scaler.gz
"""
import argparse, joblib, logging
import requests
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

SEQ_LEN = 60

def fetch_closes(symbol: str, interval="1h", limit=1000) -> np.ndarray:
    url = "https://api.binance.com/api/v3/klines"
    r = requests.get(url, params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=10)
    r.raise_for_status()
    return np.array([float(k[4]) for k in r.json()], dtype=np.float32)

def build_sequences(scaled: np.ndarray, seq_len: int):
    X, y = [], []
    for i in range(len(scaled) - seq_len):
        X.append(scaled[i:i + seq_len])
        y.append(scaled[i + seq_len])
    return np.array(X), np.array(y)

def build_model(seq_len: int) -> Sequential:
    m = Sequential([
        LSTM(64, return_sequences=True, input_shape=(seq_len, 1)),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(1)
    ])
    m.compile(optimizer="adam", loss="mse")
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol",  default="BTCUSDT")
    ap.add_argument("--interval",default="1h")
    ap.add_argument("--limit",   type=int, default=1000)
    ap.add_argument("--epochs",  type=int, default=20)
    args = ap.parse_args()

    log.info("拉取 %s %s x%d 根 K 线", args.symbol, args.interval, args.limit)
    closes = fetch_closes(args.symbol, args.interval, args.limit)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(closes.reshape(-1, 1)).flatten()

    X, y = build_sequences(scaled, SEQ_LEN)
    X = X.reshape(-1, SEQ_LEN, 1)

    split = int(len(X) * 0.9)
    X_tr, X_val = X[:split], X[split:]
    y_tr, y_val = y[:split], y[split:]

    log.info("训练集 %d  验证集 %d", len(X_tr), len(X_val))
    model = build_model(SEQ_LEN)
    model.fit(
        X_tr, y_tr,
        validation_data=(X_val, y_val),
        epochs=args.epochs,
        batch_size=32,
        callbacks=[EarlyStopping(patience=5, restore_best_weights=True)],
        verbose=1
    )

    model.save("crypto_lstm_model.h5")
    joblib.dump(scaler, "scaler.gz")
    log.info("已保存 crypto_lstm_model.h5  scaler.gz")

if __name__ == "__main__":
    main()
