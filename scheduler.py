import requests
from datetime import datetime

TOKEN = "TOKEN_BOT_KAMU"
CHAT_ID = "CHAT_ID_KAMU"

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
