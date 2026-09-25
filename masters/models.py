from django.db import models
from django.conf import settings
from django.db.models import Avg, Count


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

    # --- REYTING UCHUN YANGI MAYDONLAR ---
    avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
    )
    ratings_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username

    def recalc_rating(self):
        """Ustaning barcha review'lari asosida o'rtacha bahoni qayta hisoblaydi."""
        agg = self.reviews.aggregate(avg=Avg('rating'), cnt=Count('id'))
        self.avg_rating = agg['avg'] or 0
        self.ratings_count = agg['cnt'] or 0
        self.save(update_fields=['avg_rating', 'ratings_count'])