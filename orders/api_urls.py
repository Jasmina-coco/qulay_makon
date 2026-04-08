from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register("orders", api_views.OrderViewSet, basename="api-order")

urlpatterns = router.urls
