from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.superadmin_login, name="superadmin_login"),
    path("logout/", views.superadmin_logout, name="superadmin_logout"),
    path("", views.superadmin_main, name="superadmin_main"),
    path("create-admin/", views.sa_create_admin, name="sa_create_admin"),
    path("delete-admin/<int:pk>/", views.sa_delete_admin, name="sa_delete_admin"),
    path("toggle-user/<int:pk>/", views.sa_toggle_user, name="sa_toggle_user"),
    path("save-settings/", views.sa_save_settings, name="sa_save_settings"),
    path("approve-product/<int:pk>/", views.sa_approve_product, name="sa_approve_product"),
    path("reject-product/<int:pk>/", views.sa_reject_product, name="sa_reject_product"),
    path("fix-order/<int:pk>/", views.sa_fix_order, name="sa_fix_order"),
    path("approve-seller/<int:pk>/", views.sa_approve_seller, name="sa_approve_seller"),
    path("change-role/<int:pk>/", views.sa_change_user_role, name="sa_change_role"),
]
