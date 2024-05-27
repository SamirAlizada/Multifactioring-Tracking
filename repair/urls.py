from django.urls import path
from .views import *

urlpatterns = [
    path('', device_list, name='device_list'),
    path('device/<int:pk>/', device_detail, name='device_detail'),
    path('device/new/', device_new, name='device_new'),
    path('device/<int:pk>/edit/', device_edit, name='device_edit'),

    # Account
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]