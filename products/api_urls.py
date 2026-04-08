from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register("categories", api_views.CategoryViewSet, basename="api-category")
router.register("products", api_views.ProductViewSet, basename="api-product")

urlpatterns = router.urls
