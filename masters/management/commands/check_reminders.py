import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta

from orders.models import Order
from core.telegram import send_telegram_message


class Command(BaseCommand):
    help = "Eslatmalarni tekshiradi va yuboradi (doimiy ishlaydi)"

    def check_once(self):
        now = timezone.localtime()
        today = now.date()

        orders = Order.objects.filter(
            status__in=['accepted', 'in_progress'],
            time_to__isnull=False,
            reminder_sent=False,
        ).select_related('master', 'client', 'category')

        for order in orders:
            if not order.master or not order.master.telegram_id:
                continue

            end_datetime = datetime.combine(today, order.time_to)
            end_datetime = timezone.make_aware(end_datetime, now.tzinfo)

            time_left = end_datetime - now

            if timedelta(0) < time_left <= timedelta(hours=1):
                minutes_left = int(time_left.total_seconds() // 60)

                lines = []
                lines.append("Eslatma!")
                lines.append("------------------------")
                lines.append("Buyurtma: #" + str(order.id) + " - " + order.category.name)
                lines.append("Mijoz: " + order.client.username)
                lines.append("Manzil: " + order.address)
                lines.append("Bergan vaqti: " + order.time_from.strftime("%H:%M") + " - " + order.time_to.strftime("%H:%M"))
                lines.append("Qolgan vaqt: ~" + str(minutes_left) + " daqiqa")
                lines.append("------------------------")
                lines.append("Ulgurib qoling! Aks holda reyting balingiz tushishi mumkin.")

                text = chr(10).join(lines)

                send_telegram_message(order.master.telegram_id, text)

                order.reminder_sent = True
                order.save(update_fields=['reminder_sent'])

                self.stdout.write("Buyurtma #" + str(order.id) + " uchun eslatma yuborildi.")

    def handle(self, *args, **options):
        self.stdout.write("Eslatmalar tekshiruvchisi ishga tushdi (har 60 sekundda)...")

        while True:
            try:
                self.check_once()
            except Exception as e:
                self.stdout.write("DEBUG xato: " + repr(e))

            time.sleep(60)


