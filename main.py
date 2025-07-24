import requests
import pandas as pd
from datetime import datetime, timedelta
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🎯 PAIR POTENSIAL TERPILIH (Narrative AI, L1, ETF, dll)
PAIRS = [
    "FETUSDT", "SEIUSDT", "ARBUSDT", "PYTHUSDT", "PENDLEUSDT", "WLDUSDT",
    "INJUSDT", "NEARUSDT", "SUIUSDT", "SOLUSDT", "BTCUSDT", "ETHUSDT"
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

    jemput = last["RSI"] < 40 and volume >= 4000000
    trend_pos = "⬆️ Di atas EMA99" if last["close"] >= last["EMA99"] else "⬇️ Di bawah EMA99"

    entry = round(price, 4)
    tp1 = round(entry * 1.05, 4)  # +5%
    tp2 = round(entry * 1.09, 4)  # +9%

    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "volume": volume,
        "rsi": round(last["RSI"], 2),
        "entry": entry,
        "tp1": tp1,
        "tp2": tp2,
        "jemput": jemput,
        "trend": trend_pos
    }

def build_report():
    report = "📈 *Laporan Pasar Efisien*\n\n"
    jemput_alerts = []

    for symbol in PAIRS:
        try:
            data = get_pair_data(symbol)
            report += (
                f"📌 *{data['symbol']}*\n"
                f"├ 💰 Harga: ${data['price']}\n"
                f"├ 📊 24h: {data['change']}%\n"
                f"├ 🔁 Volume: {data['volume']:,}\n"
                f"├ 📉 RSI: {data['rsi']}\n"
                f"├ 🌟 Entry: ${data['entry']}\n"
                f"├ 🎯 TP1: ${data['tp1']} | TP2: ${data['tp2']}\n"
                f"└ {data['trend']}\n\n"
            )
            if data["jemput"]:
                jemput_alerts.append({
                    "symbol": data["symbol"],
                    "rsi": data["rsi"],
                    "price": data["price"],
                    "volume": data["volume"],
                    "trend": data["trend"]
                })
        except Exception as e:
            report += f"⚠️ {symbol}: {e}\n\n"

    # Urutkan Jemput Bola dari RSI terendah dan volume tertinggi
    jemput_alerts.sort(key=lambda x: (x["rsi"], -x["volume"]))
    jemput_text = ""
    for j in jemput_alerts[:2]:  # Fokus hanya 2 token terbaik
        jemput_text += (
            f"📉 *{j['symbol']}* (Jemput Bola)\n"
            f"• RSI: {j['rsi']} (Oversold)\n"
            f"• Harga: ${j['price']} | Vol: ${j['volume']:,}\n"
            f"• Posisi: {j['trend']}\n\n"
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
        title_map = {
            7: "🌅 *Laporan Pagi*",
            12: "☀️ *Laporan Siang*",
            18: "🌇 *Laporan Sore*",
            22: "🌙 *Laporan Malam*"
        }
        report, jemput = build_report()
        send_message(f"{title_map[now_wib.hour]}\n\n{report}")
        if jemput:
            send_message("🧲 *2 Sinyal Jemput Bola Terbaik:*\n\n" + jemput)
