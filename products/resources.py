from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from .models import Category, Product


class ProductResource(resources.ModelResource):
    category = fields.Field(
        column_name="category",
        attribute="category",
        widget=ForeignKeyWidget(Category, field="name"),
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "discount_price",
            "stock",
            "category",
            "status",
            "is_featured",
            "created_at",
        )
        export_order = (
            "id",
            "name",
            "category",
            "price",
            "discount_price",
            "stock",
            "status",
            "is_featured",
            "created_at",
        )
        import_id_fields = ("id",)
        skip_unchanged = True


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "is_active", "created_at")
        import_id_fields = ("id",)
