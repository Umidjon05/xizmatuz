from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MasterProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'parent']


@admin.register(MasterProfile)
class MasterProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_categories', 'status_badge', 'experience_years', 'location']
    list_filter = ['status', 'categories']
    search_fields = ['user__username', 'user__phone']
    actions = ['approve_masters', 'reject_masters']

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = "Kategoriyalar"

    def status_badge(self, obj):
        colors = {'pending': 'orange', 'approved': 'green', 'rejected': 'red'}
        labels = {'pending': 'Kutilmoqda', 'approved': 'Qabul qilingan', 'rejected': 'Rad etilgan'}
        color = colors.get(obj.status, 'gray')
        label = labels.get(obj.status, obj.status)
        return format_html('<b style="color: {};">{}</b>', color, label)
    status_badge.short_description = "Holati"

    def approve_masters(self, request, queryset):
        for profile in queryset:
            profile.status = 'approved'
            profile.is_verified = True
            profile.save()
            profile.user.is_active = True
            profile.user.save()
        self.message_user(request, f"{queryset.count()} ta usta qabul qilindi.")
    approve_masters.short_description = "✅ Tanlangan ustalarni qabul qilish"

    def reject_masters(self, request, queryset):
        for profile in queryset:
            profile.status = 'rejected'
            profile.save()
            profile.user.is_active = False
            profile.user.save()
        self.message_user(request, f"{queryset.count()} ta usta rad etildi.")
    reject_masters.short_description = "❌ Tanlangan ustalarni rad etish"