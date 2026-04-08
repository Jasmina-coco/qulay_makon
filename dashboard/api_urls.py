from django.urls import path

from . import api_views

urlpatterns = [
    path("stats/", api_views.api_stats, name="api-stats"),
    path("monthly-revenue/", api_views.api_monthly_revenue, name="api-monthly-revenue"),
    path("order-status-chart/", api_views.api_order_status_chart, name="api-order-status-chart"),
    path("top-products/", api_views.api_top_products, name="api-top-products"),
]
