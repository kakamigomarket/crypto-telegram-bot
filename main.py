import requests
import pandas as pd
from datetime import datetime, timedelta
import os


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PAIRS = [ 
"BTCUSDT", "PEPEUSDT", "FETUSDT", "SEIUSDT", "SOLUSDT", 
"SUIUSDT", "XRPUSDT", "BNBUSDT", "ETHUSDT", "NMRUSDT", 
"WUSDT", "JTOUSDT", "ONDOUSDT", "POLYXUSDT", "TRUUSDT", 
"GUNUSDT", "CGPTUSDT", "ZROUSDT", "DOGEUSDT", "SHIBUSDT", 
"WIFUSDT", "LINKUSDT", "FILUSDT", "AWEUSDT", "NEIROUSDT", 
"FIDAUSDT", "JUPUSDT", "NEWTUSDT", "TONUSDT", "TRXUSDT", 
"AVAXUSDT", "HBARUSDT", "DOTUSDT", "UNIUSDT", "AAVEUSDT", 
"TAOUSDT", "NEARUSDT", "ICPUSDT", "RENDERUSDT", "VIRTUALUSDT", 
"TRUMPUSDT", "BONKUSDT", "SPXUSDT", "PENGUUSDT", "VETUSDT", 
"ALGOUSDT" 
  
]

def get_klines(symbol, interval="1h", limit=100):
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
    highs = candles[2].astype(float)
    df = pd.DataFrame({
        "close": closes,
        "high": highs
    })
    df["EMA7"] = df["close"].ewm(span=7).mean()
    df["EMA25"] = df["close"].ewm(span=25).mean()
    df["RSI"] = calc_rsi(df["close"])

    last = df.iloc[-1]
    prev_high = df["high"].iloc[-25:-1].max()
    signal = ""
    jemput = False

    if (
        last["close"] > prev_high and
        last["EMA7"] > last["EMA25"] and
        last["RSI"] > 60
    ):
        signal = "🚨 *Breakout Signal*"

    if last["RSI"] < 40:
        jemput = True

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
        "signal": signal,
        "jemput": jemput
    }

def build_report():
    report = "📊 *Laporan Pasar Otomatis*\n\n"
    breakout_alerts = []
    jemput_alerts = []

    for symbol in PAIRS:
        try:
            data = get_pair_data(symbol)
            report += (
                f"📌 *{data['symbol']}*\n"
                f"├ 💰 Harga: ${data['price']}\n"
                f"├ 📈 24h: {data['change']}%\n"
                f"├ 🔄 Volume: {data['volume']:,.0f}\n"
                f"├ 📊 RSI: {data['rsi']}\n"
                f"├ 🎯 Entry: ${data['entry']}\n"
                f"├ 🎯 TP1: ${data['tp1']} | TP2: ${data['tp2']}\n"
                f"└──────────────\n\n"
            )
            if data["signal"]:
                breakout_alerts.append(
                    f"{data['signal']}: *{data['symbol']}*\n"
                    f"• Harga: ${data['price']} (+{data['change']}%)\n"
                    f"• RSI: {data['rsi']} | Vol: ${data['volume']:,.0f}\n"
                    f"• EMA7 > EMA25 ✅ | Break High 24h ✅\n"
                )
            if data["jemput"]:
                jemput_alerts.append({
                    "symbol": data["symbol"],
                    "rsi": data["rsi"],
                    "price": data["price"],
                    "volume": data["volume"]
                })

        except Exception as e:
            report += f"⚠️ {symbol}: {e}\n\n"

   
    jemput_alerts.sort(key=lambda x: x["rsi"])
    jemput_text = ""
    for j in jemput_alerts:
        jemput_text += (
            f"📉 *Jemput Bola*: *{j['symbol']}*\n"
            f"• RSI: {j['rsi']} (Oversold)\n"
            f"• Harga: ${j['price']} | Vol: ${j['volume']:,.0f}\n\n"
        )

    return report, "\n".join(breakout_alerts), jemput_text

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

if __name__ == "__main__":
    now_wib = datetime.utcnow() + timedelta(hours=7)
    if now_wib.hour in [7, 12, 18]:
        if now_wib.hour == 7:
            title = "🌅 *Laporan Pagi*"
        elif now_wib.hour == 12:
            title = "☀️ *Laporan Siang*"
        else:
            title = "🌇 *Laporan Sore*"

        report, breakout, jemput = build_report()
        send_message(f"{title}\n\n{report}")
        if breakout:
            send_message("📢 *Sinyal Breakout:*\n\n" + breakout)
        if jemput:
            send_message("🧲 *Strategi Jemput Bola (RSI < 40):*\n\n" + jemput)
