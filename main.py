import requests
from datetime import datetime, timedelta

# Ganti dengan data bot kamu
TOKEN = "7843209309:AAHT95IIJ0hQ6kHOC8crQtMYbOldb-BQH9w"
CHAT_ID = "6152549114"

# Pair dan konfigurasi
pairs = [
    "BTCUSDT", "PEPEUSDT", "FETUSDT", "SEIUSDT",
    "SOLUSDT", "SUIUSDT", "XRPUSDT", "BNBUSDT", "ETHUSDT"
]

def get_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    res = requests.get(url).json()

    last_price = float(res['lastPrice'])
    change_percent = float(res['priceChangePercent'])
    volume = float(res['volume'])

    # Hitung RSI manual (ambil 100 candle terakhir)
    klines_url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
    candles = requests.get(klines_url).json()
    closes = [float(k[4]) for k in candles]

    gains, losses = [], []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i-1]
        if delta > 0:
            gains.append(delta)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-delta)

    avg_gain = sum(gains[-14:]) / 14
    avg_loss = sum(losses[-14:]) / 14
    rs = avg_gain / avg_loss if avg_loss != 0 else 100
    rsi = 100 - (100 / (1 + rs))

    return {
        "price": last_price,
        "change": change_percent,
        "volume": volume,
        "rsi": round(rsi, 2)
    }

def format_report():
    report = "📊 *Laporan Pasar Otomatis*\n\n"
    for symbol in pairs:
        try:
            data = get_binance_data(symbol)
            price = data["price"]
            change = data["change"]
            volume = data["volume"]
            rsi = data["rsi"]

            entry = round(price, 4)
            tp1 = round(price * 1.05, 4)
            tp2 = round(price * 1.10, 4)

            report += (
                f"📌 *{symbol}*\n"
                f"├ 💰 Harga: ${price}\n"
                f"├ 📈 24h Change: {change:.2f}%\n"
                f"├ 🔄 Volume: {volume:,.0f}\n"
                f"├ 📊 RSI: {rsi}\n"
                f"├ 🎯 Entry: ${entry}\n"
                f"├ 🎯 TP1: ${tp1} | TP2: ${tp2}\n"
                f"└──────────────\n\n"
            )
        except Exception as e:
            report += f"⚠️ Gagal ambil data {symbol}: {e}\n\n"
    return report

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# Cek jam dan kirim otomatis sesuai jadwal
now_utc = datetime.utcnow()
now_wib = now_utc + timedelta(hours=7)
hour = now_wib.hour

if hour in [7, 18]:
    pesan = format_report()
    prefix = "🌅 *Laporan Pagi*" if hour == 7 else "🌇 *Laporan Sore*"
    send_to_telegram(f"{prefix}\n\n{pesan}")
