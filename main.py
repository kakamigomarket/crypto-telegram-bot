import requests
import pandas as pd
from datetime import datetime, timedelta
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PAIRS = [
  "FUNUSDT","PROMUSDT","IMXUSDT","HIFIUSDT","PHAUSDT","RLCUSDT","MOVRUSDT",
    "PHBUSDT","OGNUSDT","HBARUSDT","INJUSDT","ICPUSDT","FETUSDT","FILUSDT","SUIUSDT","SEIUSDT","ONDOUSDT",
    "JTOUSDT","ZROUSDT","TRUUSDT","POLYXUSDT","CGPTUSDT","APTUSDT","NEARUSDT","RENDERUSDT","LINKUSDT","POLUSDT",
    "DOTUSDT","VETUSDT","BTCUSDT"
]

def get_klines(symbol, interval="4h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    return pd.DataFrame(requests.get(url).json())

def calc_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean().replace(0, 1e-6)
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_pair_data(symbol):
    ticker_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    ticker = requests.get(ticker_url).json()
    price = float(ticker["lastPrice"])
    change = float(ticker["priceChangePercent"])
    volume = float(ticker["quoteVolume"])

    candles = get_klines(symbol)
    closes = candles[4].astype(float)
    df = pd.DataFrame({"close": closes})
    df["EMA7"] = df["close"].ewm(span=7).mean()
    df["EMA25"] = df["close"].ewm(span=25).mean()
    df["EMA99"] = df["close"].ewm(span=99).mean()
    df["RSI"] = calc_rsi(df["close"])

    last = df.iloc[-1]

    jemput = last["RSI"] < 40 and volume >= 20000000 and last["close"] >= last["EMA99"]

    entry = round(price, 4)
    tp1 = round(entry * 1.05, 4)
    tp2 = round(entry * 1.10, 4)

    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "volume": volume,
        "rsi": round(last["RSI"], 2),
        "entry": entry,
        "tp1": tp1,
        "tp2": tp2,
        "jemput": jemput
    }

def build_report():
    report = "\ud83d\udcc8 *Laporan Pasar Otomatis*\n\n"
    jemput_alerts = []

    for symbol in PAIRS:
        try:
            data = get_pair_data(symbol)
            report += (
                f"\ud83d\udccc *{data['symbol']}*\n"
                f"\u251c \ud83d\udcb0 Harga: ${data['price']}\n"
                f"\u251c \ud83d\udcc8 24h: {data['change']}%\n"
                f"\u251c \ud83d\udd04 Volume: {data['volume']:,}\n"
                f"\u251c \ud83d\udcca RSI: {data['rsi']}\n"
                f"\u251c \ud83c\udf1f Entry: ${data['entry']}\n"
                f"\u251c \ud83c\udf1f TP1: ${data['tp1']} | TP2: ${data['tp2']}\n"
                f"\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n\n"
            )
            if data["jemput"]:
                jemput_alerts.append({
                    "symbol": data["symbol"],
                    "rsi": data["rsi"],
                    "price": data["price"],
                    "volume": data["volume"]
                })

        except Exception as e:
            report += f"\u26a0\ufe0f {symbol}: {e}\n\n"

    jemput_alerts.sort(key=lambda x: x["rsi"])
    jemput_text = ""
    for j in jemput_alerts:
        jemput_text += (
            f"\ud83d\udcc9 *Jemput Bola*: *{j['symbol']}*\n"
            f"\u2022 RSI: {j['rsi']} (Oversold)\n"
            f"\u2022 Harga: ${j['price']} | Vol: ${j['volume']:,}\n\n"
        )

    return report, jemput_text

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

if __name__ == "__main__":
    now_wib = datetime.utcnow() + timedelta(hours=7)
    if now_wib.hour in [7, 12, 18, 22]:
        if now_wib.hour == 7:
            title = "\ud83c\udf05 *Laporan Pagi*"
        elif now_wib.hour == 12:
            title = "\u2600\ufe0f *Laporan Siang*"
        elif now_wib.hour == 18:
            title = "\ud83c\udf07 *Laporan Sore*"
        elif now_wib.hour == 22:
            title = "\ud83c\udf19 *Laporan Malam*"

        report, jemput = build_report()
        send_message(f"{title}\n\n{report}")
        if jemput:
            send_message("\ud83e\uddf2 *Strategi Jemput Bola (RSI < 40):*\n\n" + jemput)
