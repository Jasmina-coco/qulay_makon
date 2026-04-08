from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from marketplace.permissions import IsAdminOrReadOnly

from .models import Category, Product, ProductImage
from .serializers import (
    CategoryDetailSerializer,
    CategoryListSerializer,
    CategoryWriteSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductListSerializer,
    ProductWriteSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["is_active", "parent"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return CategoryWriteSerializer
        return CategoryDetailSerializer

    @action(detail=True, methods=["get"])
    def products(self, request, pk=None):
        category = self.get_object()
        products = Product.objects.filter(category=category, status="active")
        serializer = ProductListSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category", "seller").all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["status", "category", "is_featured", "seller"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "views_count", "stock"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ProductWriteSerializer
        return ProductDetailSerializer

    @action(detail=True, methods=["get", "post"], parser_classes=[MultiPartParser, FormParser])
    def images(self, request, pk=None):
        product = self.get_object()
        if request.method == "GET":
            images = product.images.all()
            return Response(ProductImageSerializer(images, many=True).data)
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path="images/(?P<img_id>[^/.]+)")
    def delete_image(self, request, pk=None, img_id=None):
        product = self.get_object()
        try:
            img = product.images.get(id=img_id)
            img.delete()
            return Response({"success": True})
        except ProductImage.DoesNotExist:
            return Response({"error": "Rasm topilmadi"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def toggle_featured(self, request, pk=None):
        product = self.get_object()
        product.is_featured = not product.is_featured
        product.save()
        return Response({"id": product.id, "is_featured": product.is_featured})
