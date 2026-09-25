from django.db import models
from django.conf import settings

from orders.models import Order
from masters.models import MasterProfile


class Review(models.Model):
    """Mijoz ish tugagandan (Order.status == 'completed') keyin ustaga qo'yadigan baho."""

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='review',
        help_text="Har bir buyurtma faqat bitta baho olishi mumkin",
    )
    master = models.ForeignKey(
        MasterProfile,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='given_reviews',
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Baho'
        verbose_name_plural = 'Baholar'

    def __str__(self):
        return f"{self.master} — {self.rating}★"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.master.recalc_rating()

    def delete(self, *args, **kwargs):
        master = self.master
        super().delete(*args, **kwargs)
        master.recalc_rating()