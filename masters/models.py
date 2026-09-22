
from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    icon = models.CharField(
        max_length=10,
        blank=True
    )  # emoji saqlash uchun
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class MasterProfile(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('approved', 'Qabul qilingan'),
        ('rejected', 'Rad etilgan'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    categories = models.ManyToManyField(
        Category,
        related_name='masters'
    )

    experience_years = models.PositiveIntegerField(default=0)

    bio = models.TextField(blank=True)

    price_range = models.CharField(
        max_length=100,
        blank=True
    )

    work_start_time = models.TimeField(
        null=True,
        blank=True
    )

    work_end_time = models.TimeField(
        null=True,
        blank=True
    )

    location = models.CharField(
        max_length=100,
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    avatar = models.ImageField(
        upload_to='masters/',
        blank=True,
        null=True
    )

    # Telegram bilan bog'lash uchun
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True
    )

    telegram_username = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username

