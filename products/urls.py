from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/search/', views.search, name='search'),
    path('products/category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/review/', views.submit_review, name='submit_review'),
]
