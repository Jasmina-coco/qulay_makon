from django.contrib import admin

from .models import Banner, ContactMessage, MenuItem, News, NewsCategory, Page


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active", "order"]
    list_editable = ["is_active", "order"]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "is_active"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "is_active", "created_at"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "subject", "is_read", "created_at"]
    list_filter = ["is_read"]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["title", "url", "parent", "order", "is_active"]
    list_editable = ["order", "is_active"]
