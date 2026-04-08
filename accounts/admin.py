from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, SellerProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_active", "is_verified")
    list_filter = ("role", "is_active", "is_verified")
    search_fields = ("username", "email", "phone")
    fieldsets = UserAdmin.fieldsets + (
        ("Marketplace", {"fields": ("phone", "role", "avatar", "is_verified")}),
    )


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("shop_name", "user", "rating", "balance", "is_approved")
    list_filter = ("is_approved",)
    search_fields = ("shop_name", "user__username")
