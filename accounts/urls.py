from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("users/", views.user_list, name="user_list"),
    path("users/<int:user_id>/", views.user_detail, name="user_detail"),
    path("users/<int:user_id>/toggle/", views.user_toggle_active, name="user_toggle_active"),
    path("sellers/", views.seller_list, name="seller_list"),
    path("sellers/<int:seller_id>/approve/", views.seller_approve, name="seller_approve"),
]
