import requests
import pandas as pd
import time

# TOKEN & CHAT_ID Telegram kamu
TOKEN = "7843209309:AAHT95IIJ0hQ6kHOC8crQtMYbOldb-BQH9w"
CHAT_ID = "6152549114"

def fetch_binance_data(symbol="FETUSDT", interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["close"] = pd.to_numeric(df["close"])
    df["volume"] = pd.to_numeric(df["volume"])
    return df

def analyze_rsi(df, period=14):
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def run_report():
    symbols = ["FETUSDT", "SEIUSDT", "ARUSDT"]
    report = "🧠 *Laporan Strategi Otomatis Binance*\n\n"
    for sym in symbols:
        df = fetch_binance_data(symbol=sym)
        rsi = analyze_rsi(df)
        last_price = df["close"].iloc[-1]
        report += f"• *{sym.replace('USDT','')}/USDT* → Price: ${last_price:.4f} | RSI: {rsi}\n"

    report += "\n📆 Auto Report - Data Real-Time dari Binance"
    send_telegram_message(report)

run_report()
