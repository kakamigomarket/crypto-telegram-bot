import requests
from datetime import datetime, timezone

# Ganti dengan token dan chat_id kamu
TOKEN = "7843209309:AAHT95IIJ0hQ6kHOC8crQtMYbOldb-BQH9w"
CHAT_ID = "6152549114"

def sendTelegramMessage(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, json=payload)

# Waktu sekarang dalam UTC, tambahkan +7 jam (WIB)
now_utc = datetime.now(timezone.utc)
hour = now_utc.hour + 7
minute = now_utc.minute

print(f"Bot dijalankan pada jam {hour}:{minute} WIB")

# Kirim pesan jika tepat jam 07:30 WIB
if hour == 7 and minute == 30:
    sendTelegramMessage("🌅 *Laporan Pagi Otomatis*\n\n(scan pagi otomatis dikirim)")
# Kirim pesan jika tepat jam 18:30 WIB
elif hour == 18 and minute == 30:
    sendTelegramMessage("🌆 *Laporan Sore Otomatis*\n\n(scan sore otomatis dikirim)")
