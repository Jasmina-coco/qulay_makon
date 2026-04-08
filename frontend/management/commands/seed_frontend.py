from django.core.management.base import BaseCommand
from django.utils.text import slugify

from frontend.models import Banner, MenuItem, News, NewsCategory, Page


class Command(BaseCommand):
    help = "Seed frontend demo content"

    def handle(self, *args, **options):
        for i in range(1, 6):
            Banner.objects.get_or_create(
                title=f"Banner {i}",
                defaults={
                    "subtitle": f"Banner subtitle {i}",
                    "image": "banners/demo.jpg",
                    "link": "",
                    "is_active": True,
                    "order": i,
                },
            )

        pages = [
            ("Biz haqimizda", "about"),
            ("Yetkazib berish", "delivery"),
            ("To'lov", "payment"),
            ("Savol-javob", "faq"),
            ("Privacy", "privacy"),
        ]
        for title, slug in pages:
            Page.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "content": f"{title} sahifasi matni",
                    "meta_description": title,
                    "is_active": True,
                },
            )

        cat1, _ = NewsCategory.objects.get_or_create(name="Yangiliklar", defaults={"slug": "yangiliklar"})
        cat2, _ = NewsCategory.objects.get_or_create(name="Aksiyalar", defaults={"slug": "aksiyalar"})
        categories = [cat1, cat2]

        for i in range(1, 11):
            title = f"Yangilik {i}"
            News.objects.get_or_create(
                slug=slugify(title),
                defaults={
                    "title": title,
                    "category": categories[i % 2],
                    "short_description": "Qisqa tavsif",
                    "content": f"{title} uchun to'liq matn",
                    "is_active": True,
                },
            )

        menu_items = [
            ("Bosh sahifa", "/"),
            ("Katalog", "/catalog/"),
            ("Yangiliklar", "/news/"),
            ("Biz haqimizda", "/page/about/"),
            ("Yetkazib berish", "/page/delivery/"),
            ("To'lov", "/page/payment/"),
            ("FAQ", "/page/faq/"),
            ("Kontakt", "/contact/"),
        ]
        for idx, (title, url) in enumerate(menu_items, start=1):
            MenuItem.objects.get_or_create(
                title=title,
                defaults={"url": url, "order": idx, "is_active": True},
            )

        self.stdout.write(self.style.SUCCESS("Frontend demo ma'lumotlar yaratildi"))
