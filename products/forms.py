from django import forms

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
