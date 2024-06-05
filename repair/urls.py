from django.urls import path
from .views import *

urlpatterns = [
    #Add
    path('device/add/', add_device, name='add_device'),
    path('add-product/', add_product, name='add_product'),
    path('add-product-sold/', add_product_sold, name='add_product_sold'),
    path('ajax/load-products/', load_products, name='load_products'),

    #List
    path('device/', device_list, name='device_list'),
    path('product-list/', product_list, name='product_list'),
    path('product-sold-list/', product_sold_list, name='product_sold_list'),

    #Panel
    path('product-panel/', product_panel, name='product_panel'),
    path('product-sold-panel/', product_sold_panel, name='product_sold_panel'),

    #Delete
    path('delete-device/<int:pk>/', delete_device, name='delete_device'),
    path('delete-product/<int:pk>/', delete_product, name='delete_product'),
    path('delete-product-sold/<int:pk>/', delete_product_sold, name='delete_product_sold'),

    #Update
    path('device/<int:pk>/update/', update_device, name='update_device'),
    path('update-product/<int:pk>/', update_product, name='update_product'),
    path('update-product-sold/<int:pk>/', update_product_sold, name='update_product_sold'),
    
    # Operations
    path('increase/<int:product_id>/', increase_stock, name='increase_stock'),
    path('decrease/<int:product_id>/', decrease_stock, name='decrease_stock'),

    path('product-sold-increase/<int:pk>/', increase_sold, name='increase_sold'),
    path('product-sold-decrease/<int:pk>/', decrease_sold, name='decrease_sold'),

    path('device/<int:pk>/', device_detail, name='device_detail'),
    path('', searched_device, name='searched_device'),

    # Chart
    # path('sales-chart/', sales_chart, name='sales_chart'),
    # path('price-comparison-chart/', price_comparison_chart, name='price_comparison_chart'),
    path('combined-charts-view/', combined_charts_view, name='combined_charts_view'),



    # Account
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]