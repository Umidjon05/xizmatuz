import requests
from django.conf import settings

API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


def send_telegram_message(chat_id, text, reply_markup=None):
    try:
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup:
            import json
            data["reply_markup"] = json.dumps(reply_markup)

        requests.post(f"{API_URL}/sendMessage", data=data, timeout=10)
    except requests.RequestException:
        pass