from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('master', 'client', 'rating', 'order', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('master__user__username', 'client__username', 'comment')
    readonly_fields = ('created_at',)

# MUHIM: kim baho qo'yganini (client) FAQAT shu Django admin panelida
# (masalan /admin/) va faqat is_staff=True bo'lgan foydalanuvchi ko'radi.
# Ustalarga (User.user_type == 'master') hech qachon is_staff=True bermang
# va ularga admin panel havolasini ko'rsatmang — shunda ular bu ma'lumotga
# umuman kira olmaydi. reviews/views.py va shablonlarda "client" maydoni
# ustalarga ko'rinadigan hech qanday joyga chiqarilmaydi.