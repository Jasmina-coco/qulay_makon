from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register("users", api_views.UserViewSet, basename="api-user")
router.register("sellers", api_views.SellerViewSet, basename="api-seller")

urlpatterns = router.urls
