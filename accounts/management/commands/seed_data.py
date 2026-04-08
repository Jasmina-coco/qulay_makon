from datetime import timedelta
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import CustomUser, SellerProfile
from orders.models import Order, OrderItem
from products.models import Category, Product


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        admin, _ = CustomUser.objects.get_or_create(
            username="havo_quyoshli",
            defaults={
                "email": "admin@market.uz",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
                "is_verified": True,
            },
        )
        admin.set_password("havo_bulutli")
        admin.save()

        sellers = []
        for i in range(1, 6):
            u, _ = CustomUser.objects.get_or_create(
                username=f"seller{i}",
                defaults={"email": f"seller{i}@market.uz", "role": "seller", "is_verified": True},
            )
            u.set_password("seller123")
            u.save()
            SellerProfile.objects.get_or_create(
                user=u,
                defaults={
                    "shop_name": f"Do'kon {i}",
                    "description": f"Seller {i} do'koni",
                    "rating": round(random.uniform(3, 5), 2),
                    "balance": random.randint(100000, 5000000),
                    "is_approved": True,
                },
            )
            sellers.append(u)

        for i in range(1, 11):
            u, _ = CustomUser.objects.get_or_create(
                username=f"buyer{i}",
                defaults={"email": f"buyer{i}@market.uz", "role": "buyer"},
            )
            u.set_password("buyer123")
            u.save()

        cat_names = [
            "Elektronika",
            "Kiyim-kechak",
            "Oziq-ovqat",
            "Kitoblar",
            "Sport",
            "Uy-ro'zg'or",
            "Go'zallik",
            "Bolalar",
        ]
        cats = []
        for name in cat_names:
            c, _ = Category.objects.get_or_create(
                name=name,
                defaults={"slug": name.lower().replace("'", "").replace(" ", "-"), "is_active": True},
            )
            cats.append(c)

        product_names = [
            "Smartphone",
            "Noutbuk",
            "Kurtka",
            "Ko'ylak",
            "Non",
            "Shakar",
            "Roman kitobi",
            "Futbol to'pi",
            "Idish to'plami",
            "Krem",
            "O'yinchoq",
            "Quloqchin",
            "Soat",
            "Sumka",
            "Shim",
            "Choy",
            "Kofe",
            "Daftar",
            "Ruchka",
            "Yostiq",
            "Ko'rpa",
            "Tarelka",
            "Piyola",
            "Stakan",
            "Qoshiq",
        ]
        statuses = ["active", "active", "active", "pending", "rejected", "draft"]
        products = []
        for i in range(50):
            name = random.choice(product_names) + f" #{i + 1}"
            p, _ = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": f"{name} haqida batafsil ma'lumot",
                    "price": random.randint(10000, 5000000),
                    "discount_price": random.choice([None, None, random.randint(5000, 4000000)]),
                    "stock": random.randint(0, 500),
                    "category": random.choice(cats),
                    "seller": random.choice(sellers),
                    "status": random.choice(statuses),
                    "is_featured": random.choice([True, False, False]),
                    "views_count": random.randint(0, 10000),
                },
            )
            products.append(p)

        buyers = CustomUser.objects.filter(role="buyer")
        order_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        for _ in range(30):
            days_ago = random.randint(0, 90)
            order_date = timezone.now() - timedelta(days=days_ago)
            buyer = random.choice(list(buyers))
            order = Order.objects.create(
                user=buyer,
                total_amount=0,
                status=random.choice(order_statuses),
                address=f"Toshkent, {random.randint(1, 50)}-uy",
                phone=f"+99890{random.randint(1000000, 9999999)}",
                created_at=order_date,
            )
            total = 0
            for _ in range(random.randint(1, 4)):
                prod = random.choice(products)
                qty = random.randint(1, 5)
                price = float(prod.price)
                OrderItem.objects.create(order=order, product=prod, quantity=qty, price=price)
                total += price * qty
            order.total_amount = total
            order.save()

        self.stdout.write(self.style.SUCCESS("Demo ma'lumotlar yaratildi!"))
