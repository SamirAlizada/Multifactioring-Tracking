from django import forms
from .models import Device

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_name', 'customer_name', 'repair_cost', 'repair_duration', 'delivery_date', 'status', 'notes']