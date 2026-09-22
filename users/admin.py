from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'user_type', 'city', 'district', 'is_active', 'is_superuser']
    list_filter = ['user_type', 'is_active', 'city']
    fieldsets = UserAdmin.fieldsets + (
        ("Qo'shimcha ma'lumot", {'fields': ('user_type', 'phone', 'address', 'city', 'district', 'street', 'full_address', 'avatar')}),
    )


admin.site.register(User, CustomUserAdmin)
