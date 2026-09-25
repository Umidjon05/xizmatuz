import time
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from masters.models import MasterProfile
from orders.models import Order

API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


class Command(BaseCommand):
    help = "Telegram botdan /start master_<id> va tugma bosishlarini tinglaydi"

    def answer_callback(self, callback_id, text):
        try:
            requests.post(f"{API_URL}/answerCallbackQuery", data={
                "callback_query_id": callback_id,
                "text": text,
                "show_alert": False,
            }, timeout=10)
        except requests.RequestException:
            pass

    def send_message(self, chat_id, text):
        try:
            requests.post(f"{API_URL}/sendMessage", data={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            }, timeout=10)
        except requests.RequestException:
            pass

    def handle_callback(self, callback):
        callback_id = callback["id"]
        data = callback.get("data", "")
        chat_id = callback["from"]["id"]

        if not data.startswith("accept_order_"):
            self.answer_callback(callback_id, "Noma'lum buyruq.")
            return

        order_id = data.replace("accept_order_", "").strip()

        master = MasterProfile.objects.filter(telegram_id=chat_id).first()
        if not master:
            self.answer_callback(callback_id, "Siz ro'yxatdan o'tmagansiz.")
            return

        with transaction.atomic():
            order = Order.objects.select_for_update().filter(id=order_id).first()

            if not order:
                self.answer_callback(callback_id, "Buyurtma topilmadi.")
                return

            if order.status != 'pending':
                self.answer_callback(callback_id, "Bu buyurtma allaqachon qabul qilingan.")
                return

            if not master.categories.filter(id=order.category_id).exists():
                self.answer_callback(callback_id, "Bu buyurtma sizning kategoriyangizga mos emas.")
                return

            has_active_order = Order.objects.filter(
                master=master,
                status__in=['accepted', 'in_progress']
            ).exists()

            if has_active_order:
                self.answer_callback(
                    callback_id,
                    "Avval joriy buyurtmangizni yakunlang."
                )
                return

            order.master = master
            order.status = 'accepted'
            order.save(update_fields=['master', 'status'])

        self.answer_callback(callback_id, "✅ Buyurtma qabul qilindi!")
        self.send_message(
            chat_id,
            f"✅ <b>Siz buyurtma #{order.id} ni qabul qildingiz.</b>\n"
            f"Mijoz bilan bog'lanib, xizmatni boshlashingiz mumkin."
        )

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

                for update in data.get("result", []):
                    offset = update["update_id"] + 1

                    callback = update.get("callback_query")
                    if callback:
                        self.handle_callback(callback)
                        continue

                    message = update.get("message")
                    if not message:
                        continue

                    text = message.get("text", "")
                    chat = message["chat"]
                    chat_id = chat["id"]

                    if text.startswith("/start master_"):
                        master_id = text.replace("/start master_", "").strip()
                        master = MasterProfile.objects.filter(id=master_id).first()

                        if master:
                            master.telegram_id = chat_id
                            master.telegram_username = chat.get("username", "")
                            master.save(update_fields=['telegram_id', 'telegram_username'])

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