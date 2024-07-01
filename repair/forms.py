from django import forms
from .models import Device, Product, ProductSold, Category
from datetime import datetime, date

class CustomDateInput(forms.DateInput):
    input_type = 'text'
    format = '%d/%m/%Y'

    def __init__(self, *args, **kwargs):
        kwargs['format'] = self.format
        super().__init__(*args, **kwargs)

    def format_value(self, value):
        if value:
            if isinstance(value, (datetime, date)):
                return value.strftime(self.format)
        return value

class DeviceForm(forms.ModelForm):
    add_date = forms.CharField(widget=CustomDateInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYYY'}))

    class Meta:
        model = Device
        fields = ['device_name', 'customer_name', 'repair_cost', 'repair_duration', 'add_date', 'status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'style': 'width:100%;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # If create new form
            self.fields['add_date'].initial = date.today().strftime('%d/%m/%Y')

    def clean_add_date(self):
        add_date = self.cleaned_data['add_date']
        if isinstance(add_date, str):
            try:
                return datetime.strptime(add_date, '%d/%m/%Y').date()
            except ValueError:
                raise forms.ValidationError("Enter the date in DD/MM/YYYY format.")
        return add_date

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
    date = forms.CharField(widget=CustomDateInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYYY'}))

    class Meta:
        model = ProductSold
        fields = ['category', 'product_name', 'date', 'price', 'count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # if create new form
            self.fields['date'].initial = date.today().strftime('%d/%m/%Y')
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['product_name'].queryset = Product.objects.filter(category_name_id=category_id).order_by('product_name')
            except (ValueError, TypeError):
                self.fields['product_name'].queryset = Product.objects.none()
        elif self.instance.pk:
            self.fields['category'].initial = self.instance.product_name.category_name
            self.fields['product_name'].queryset = Product.objects.filter(category_name=self.instance.product_name.category_name).order_by('product_name')
        else:
            self.fields['product_name'].queryset = Product.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product_name')
        count = cleaned_data.get('count')

        if product and count:
            if product.stock_number < count:
                raise forms.ValidationError(f"Only {product.stock_number} products are in stock.")
        return cleaned_data

    def clean_date(self):
        date_str = self.cleaned_data['date']
        if isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, '%d/%m/%Y').date()
            except ValueError:
                raise forms.ValidationError("Enter the date in DD/MM/YYYY format.")
        return date_str