from django.contrib import admin
from .models import Device, Product, ProductSold, Category

admin.site.register(Device)
admin.site.register(Product)
admin.site.register(ProductSold)
admin.site.register(Category)