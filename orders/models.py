from django.db import models

from accounts.models import CustomUser
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Kutilmoqda"),
        ("processing", "Jarayonda"),
        ("shipped", "Yetkazilmoqda"),
        ("delivered", "Yetkazildi"),
        ("cancelled", "Bekor qilindi"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    address = models.TextField()
    phone = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        product_name = self.product.name if self.product else "Deleted product"
        return f"{product_name} x {self.quantity}"
