from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("api/stats/", views.api_dashboard_stats, name="api_stats"),
    path("api/global-search/", views.api_global_search, name="api_global_search"),
    path("api/monthly-revenue/", views.api_monthly_revenue, name="api_monthly_revenue"),
    path("api/order-status-chart/", views.api_order_status_chart, name="api_order_status"),
    path("api/top-products/", views.api_top_products, name="api_top_products"),
]
