from django.urls import path

from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("export/", views.product_export, name="product_export"),
    path("import/", views.product_import, name="product_import"),
    path("create/", views.product_create, name="product_create"),
    path("<int:product_id>/", views.product_detail, name="product_detail"),
    path("<int:product_id>/edit/", views.product_edit, name="product_edit"),
    path("<int:product_id>/delete/", views.product_delete, name="product_delete"),
    path("<int:product_id>/approve/", views.product_approve, name="product_approve"),
    path(
        "<int:product_id>/images/upload/",
        views.product_image_upload,
        name="product_image_upload",
    ),
    path(
        "<int:product_id>/images/<int:image_id>/delete/",
        views.product_image_delete,
        name="product_image_delete",
    ),
    path(
        "<int:product_id>/images/<int:image_id>/set-main/",
        views.product_image_set_main,
        name="product_image_set_main",
    ),
    path("categories/", views.category_list, name="category_list"),
    path("categories/export/", views.category_export, name="category_export"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/<int:category_id>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:category_id>/delete/", views.category_delete, name="category_delete"),
]
