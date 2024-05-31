from django import forms
from .models import Device, Product, ProductSold

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_name', 'customer_name', 'repair_cost', 'repair_duration', 'add_date', 'status', 'notes']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'price', 'stock_number']

class ProductSoldForm(forms.ModelForm):
    class Meta:
        model = ProductSold
        fields = ['product_name', 'date', 'price', 'count']

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product_name')
        count = cleaned_data.get('count')

        if product and count:
            if product.stock_number < count:
                raise forms.ValidationError(f"Only {product.stock_number} items available in stock.")
        return cleaned_data