from django import forms
from .models import Device, Product, ProductSold, Category
from datetime import datetime

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_name', 'customer_name', 'repair_cost', 'repair_duration', 'add_date', 'status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'style': 'width:100%;'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category_name', 'product_name', 'price', 'stock_number']

class ProductSoldForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)

    class Meta:
        model = ProductSold
        fields = ['category', 'product_name', 'date', 'price', 'count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['product_name'].queryset = Product.objects.filter(category_name_id=category_id).order_by('product_name')
            except (ValueError, TypeError):
                self.fields['product_name'].queryset = Product.objects.none()
        elif self.instance.pk:
            # Set the initial value for category based on the product's category
            self.fields['category'].initial = self.instance.product_name.category_name
            # Filter product_name queryset based on the current category
            self.fields['product_name'].queryset = Product.objects.filter(category_name=self.instance.product_name.category_name).order_by('product_name')
        else:
            self.fields['product_name'].queryset = Product.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product_name')
        count = cleaned_data.get('count')

        if product and count:
            if product.stock_number < count:
                raise forms.ValidationError(f"Only {product.stock_number} items available in stock.")
        return cleaned_data