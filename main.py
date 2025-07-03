import requests

TOKEN = "7843209309:AAHT95IIJ0hQ6kHOC8crQtMYbOldb-BQH9w"
CHAT_ID = "6152549114"

def send_telegram_message():
    message = (
        "🧠 *Laporan Strategi Crypto Hari Ini*\n\n"
        "• *FET/USDT* → Entry: $0.720 | TP: $0.78\n"
        "• *SUI/USDT* → Entry: $2.90 | TP: $3.25\n\n"
        "Pantau RSI & Volume. TP bertahap 💹"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

send_telegram_message()
