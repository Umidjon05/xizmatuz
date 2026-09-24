from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('client', 'Mijoz'),
        ('master', 'Usta'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)          # Viloyat/shahar
    district = models.CharField(max_length=100, blank=True)       # Tuman
    street = models.CharField(max_length=255, blank=True)         # Ko'cha
    full_address = models.CharField(max_length=500, blank=True)   # To'liq manzil (avtomatik)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    telegram_chat_id = models.CharField(max_length=32, blank=True, null=True)
    telegram_link_code = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"