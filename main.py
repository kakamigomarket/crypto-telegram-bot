
import requests
import time
import pandas as pd

TOKEN = "7843209309:AAHT95IIJ0hQ6kHOC8crQtMYbOldb-BQH9w"
CHAT_ID = "6152549114"

PAIRS = ["BTCUSDT", "PEPEUSDT", "FETUSDT", "SEIUSDT", "SOLUSDT", "SUIUSDT", "XRPUSDT", "BNBUSDT", "ETHUSDT"]

def sendTelegramMessage(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def get_rsi(symbol, interval="1h", period=14):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={period+1}"
    data = requests.get(url).json()
    closes = [float(k[4]) for k in data]
    df = pd.DataFrame(closes, columns=["close"])
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean().iloc[-1]
    avg_loss = loss.rolling(window=period).mean().iloc[-1]
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def get_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    r = requests.get(url).json()
    last_price = float(r["lastPrice"])
    change_percent = float(r["priceChangePercent"])
    volume = float(r["quoteVolume"])
    rsi = get_rsi(symbol)

    entry = last_price * 0.97
    tp1 = entry * 1.08
    tp2 = entry * 1.15

    return (
        f"*{symbol}*\n"
        f"• Harga: `${last_price:,.4f}`\n"
        f"• Perubahan 24h: `{change_percent:+.2f}%`\n"
        f"• Volume 24h: `${volume:,.2f}`\n"
        f"• RSI (1H): `{rsi}`\n"
        f"• Entry (jemput bola): `${entry:.4f}`\n"
        f"• TP1: `${tp1:.4f}`  |  TP2: `${tp2:.4f}`\n"
    )

def main():
    message = "🧠 *Laporan Market Otomatis Binance*\n\n"
    for pair in PAIRS:
        try:
            message += get_data(pair) + "\n"
            time.sleep(0.2)
        except Exception as e:
            message += f"⚠️ Gagal ambil data untuk {pair}: {str(e)}\n\n"
    sendTelegramMessage(message)

if __name__ == "__main__":
    main()
