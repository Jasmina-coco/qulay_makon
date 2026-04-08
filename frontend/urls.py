from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<slug:slug>/", views.category_detail, name="category_page"),
    path("product/<int:pk>/", views.product_detail, name="product_page"),
    path("news/", views.news_list, name="news_list_page"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail_page"),
    path("page/<slug:slug>/", views.page_detail, name="page_detail"),
    path("contact/", views.contact, name="contact_page"),
    path("search/", views.search, name="search_page"),
]
