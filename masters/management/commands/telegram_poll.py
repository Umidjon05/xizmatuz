import time
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from masters.models import MasterProfile

API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


class Command(BaseCommand):
    help = "Telegram botdan /start master_<id> xabarlarini tinglab, ustalarni telegram_id bilan bog'laydi"

    def handle(self, *args, **options):
        offset = 0
        self.stdout.write("Telegram bot tinglanmoqda...")
        while True:
            try:
                resp = requests.get(
                    f"{API_URL}/getUpdates",
                    params={"offset": offset, "timeout": 30},
                    timeout=35,
                )
                data = resp.json()
                print("DEBUG data:", data, flush=True)

                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    message = update.get("message")
                    if not message:
                        continue

                    text = message.get("text", "")
                    chat = message["chat"]
                    chat_id = chat["id"]

                    print("DEBUG text:", repr(text), "chat_id:", chat_id, flush=True)

                    if text.startswith("/start master_"):
                        master_id = text.replace("/start master_", "").strip()
                        print("DEBUG master_id:", repr(master_id), flush=True)

                        master = MasterProfile.objects.filter(id=master_id).first()
                        print("DEBUG master found:", master, flush=True)

                        if master:
                            master.telegram_id = chat_id
                            master.telegram_username = chat.get("username", "")
                            master.save(update_fields=['telegram_id', 'telegram_username'])
                            print("DEBUG saqlandi:", master.id, master.telegram_id, flush=True)

                            requests.post(f"{API_URL}/sendMessage", data={
                                "chat_id": chat_id,
                                "text": f"Xush kelibsiz, {master.user.username}! Endi yangi buyurtmalar shu botga keladi.",
                            })
                        else:
                            requests.post(f"{API_URL}/sendMessage", data={
                                "chat_id": chat_id,
                                "text": "Havola noto'g'ri. Saytdagi profilingizdan qaytadan urinib ko'ring.",
                            })
            except Exception as e:
                print("DEBUG xato:", repr(e), flush=True)
                time.sleep(5)
