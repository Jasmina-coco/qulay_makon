from rest_framework import serializers

from .models import Category, Product, ProductImage


class CategoryListSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "image",
            "parent",
            "is_active",
            "products_count",
            "created_at",
        ]

    def get_products_count(self, obj):
        return obj.products.count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "image",
            "parent",
            "is_active",
            "children",
            "products_count",
            "created_at",
        ]

    def get_children(self, obj):
        return CategoryListSerializer(obj.children.all(), many=True).data

    def get_products_count(self, obj):
        return obj.products.count()


class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug", "image", "parent", "is_active"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_main"]


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name", read_only=True, default=None
    )
    seller_name = serializers.CharField(source="seller.username", read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "discount_price",
            "stock",
            "category",
            "category_name",
            "seller",
            "seller_name",
            "status",
            "is_featured",
            "views_count",
            "main_image",
            "created_at",
        ]

    def get_main_image(self, obj):
        img = obj.images.filter(is_main=True).first()
        if img and img.image:
            request = self.context.get("request")
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name", read_only=True, default=None
    )
    seller_name = serializers.CharField(source="seller.username", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "discount_price",
            "stock",
            "category",
            "category_name",
            "seller",
            "seller_name",
            "status",
            "is_featured",
            "views_count",
            "images",
            "created_at",
            "updated_at",
        ]


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "discount_price",
            "stock",
            "category",
            "seller",
            "status",
            "is_featured",
        ]
