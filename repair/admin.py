from django.contrib import admin
from .models import Device, Product, ProductSold

admin.site.register(Device)
admin.site.register(Product)
admin.site.register(ProductSold)