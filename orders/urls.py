from django.urls import path

from . import views

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("<int:order_id>/update-status/", views.order_update_status, name="order_update_status"),
    path("<int:order_id>/delete/", views.order_delete, name="order_delete"),
]
