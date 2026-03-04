from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:id>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:id>/toggle/', views.product_toggle, name='product_toggle'),
    
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:id>/', views.order_detail, name='order_detail'),
    path('orders/<int:id>/status/', views.order_status, name='order_status'),
    
    path('users/', views.user_list, name='user_list'),
    path('users/<int:id>/', views.user_detail, name='user_detail'),
    
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:id>/delete/', views.category_delete, name='category_delete'),
    
    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupons/add/', views.coupon_add, name='coupon_add'),
    path('coupons/<int:id>/edit/', views.coupon_edit, name='coupon_edit'),
    path('coupons/<int:id>/delete/', views.coupon_delete, name='coupon_delete'),
    path('coupons/<int:id>/toggle/', views.coupon_toggle, name='coupon_toggle'),
    
    path('stats/revenue/', views.revenue_stats, name='revenue_stats'),
]
