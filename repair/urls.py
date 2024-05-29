from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('device/', device_list, name='device_list'),
    path('device/<int:pk>/', device_detail, name='device_detail'),
    path('', searched_device, name='searched_device'),
    path('device/add/', add_device, name='add_device'),
    path('device/<int:pk>/update/', update_device, name='update_device'),
    path('delete-device/<int:pk>/', delete_device, name='delete_device'),

    # Account
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]