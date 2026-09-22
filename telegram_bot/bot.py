import os
import sys

import django


# Xizmat Uz loyihasining asosiy papkasi
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Django'ni ishga tushirish
django.setup()


from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from masters.models import MasterProfile


# Bot tokeni
TOKEN = "8955274024:AAGpZgKT9yAnJxdvidN2rmMSSMtogFQrAUs"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user

    # /start dan keyingi ma'lumot
    # Masalan: /start master_15
    args = context.args

    # Oddiy /start
    if not args:
        await update.message.reply_text(
            "Assalomu alaykum! 👋\n\n"
            "Xizmat Uz botiga xush kelibsiz.\n\n"
            "Agar siz usta bo'lsangiz, "
            "saytdagi Telegram orqali ulanish tugmasidan foydalaning."
        )
        return

    start_data = args[0]

    # master_15 -> 15
    if not start_data.startswith("master_"):
        await update.message.reply_text(
            "❌ Noto'g'ri ulanish havolasi."
        )
        return

    try:
        master_id = int(
            start_data.replace("master_", "")
        )
    except ValueError:
        await update.message.reply_text(
            "❌ Usta ID noto'g'ri."
        )
        return

    # Ustani topamiz
    try:
        master = MasterProfile.objects.get(
            id=master_id
        )
    except MasterProfile.DoesNotExist:
        await update.message.reply_text(
            "❌ Bunday usta topilmadi."
        )
        return

    # Telegram ma'lumotlarini saqlaymiz
    master.telegram_id = telegram_user.id
    master.telegram_username = telegram_user.username

    master.save(
        update_fields=[
            "telegram_id",
            "telegram_username",
        ]
    )

    await update.message.reply_text(
        f"✅ Telegram muvaffaqiyatli ulandi!\n\n"
        f"👨‍🔧 Usta: {master.user.username}\n"
        f"🔧 Xizmat Uz akkauntingiz Telegram bilan bog'landi.\n\n"
        f"Endi sizga yangi zakazlar Telegram orqali yuboriladi."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    print("Xizmat Uz Telegram bot ishga tushdi...")

    app.run_polling()


if __name__ == "__main__":
    main()

