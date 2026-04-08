from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("super-admin/", include("superadmin.urls")),
    path("admin-panel/", include("dashboard.urls")),
    path("admin-panel/accounts/", include("accounts.urls")),
    path("admin-panel/products/", include("products.urls")),
    path("admin-panel/orders/", include("orders.urls")),
    path("api/v1/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/v1/dashboard/", include("dashboard.api_urls")),
    path("api/v1/", include("products.api_urls")),
    path("api/v1/", include("orders.api_urls")),
    path("api/v1/", include("accounts.api_urls")),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("", include("frontend.urls")),
]

urlpatterns += [
    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
