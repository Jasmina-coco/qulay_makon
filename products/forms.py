from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Category, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "name",
            "description",
            "price",
            "discount_price",
            "stock",
            "category",
            "seller",
            "status",
            "is_featured",
        )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "slug", "image", "parent", "is_active")
        labels = {
            "name": _("Nomi"),
            "slug": _("Slug"),
            "image": _("Rasm"),
            "parent": _("Parent"),
            "is_active": _("Faol holat"),
        }
