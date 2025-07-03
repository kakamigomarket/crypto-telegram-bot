import requests
from datetime import datetime

TOKEN = "7843209309:AAHT95IIJ0hQ6kHOC8crQtMYbOldb-BQH9w"
CHAT_ID = "6152549114"

def sendTelegramMessage(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, json=payload)

# Cek waktu lokal Indonesia (UTC+7)
now = datetime.utcnow().hour + 7

if now == 7:
    sendTelegramMessage("📊 *Laporan Pagi Otomatis*\n\n(scan pagi otomatis dikirim)")
elif now == 18:
    sendTelegramMessage("📊 *Laporan Sore Otomatis*\n\n(scan sore otomatis dikirim)")



sendTelegramMessage("🔥 Uji coba kirim pesan Telegram berhasil!")
