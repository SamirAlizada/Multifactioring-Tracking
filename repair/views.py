from django.shortcuts import render, get_object_or_404, redirect
from .models import Device
from .forms import DeviceForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import datetime, date, timedelta
import logging
from django.contrib.auth.decorators import login_required

@login_required
def device_list(request):
    today = date.today()
    
    # Retrieve the search query
    query = request.GET.get('q')
    
    # Get all devices or filter based on the search query
    devices = Device.objects.all()
    if query:
        devices = devices.filter(device_name__icontains=query)
    
    # Dictionary to group devices by month
    grouped_devices_dict = {}

    # Grouping devices by month key and calculating total repair costs
    for device in devices:
        # Create month and year key from the registration date
        month_key = device.add_date.strftime('%Y-%m')
        month_display = device.add_date.strftime('%B %Y')

        # Group by month key
        if month_key not in grouped_devices_dict:
            grouped_devices_dict[month_key] = {
                'display': month_display,
                'devices': [],
                'total_repair_cost': 0  # Track total monthly repair costs
            }

        # Add the device to the corresponding month's group
        grouped_devices_dict[month_key]['devices'].append(device)

        # Add the device's repair cost to the total repair cost for the month
        grouped_devices_dict[month_key]['total_repair_cost'] += device.repair_cost

    # Convert dictionary to a list and sort by key in descending order
    sorted_grouped_devices_list = sorted(
        grouped_devices_dict.items(),
        key=lambda x: x[0],
        reverse=True
    )

    # Convert sorted list back to dictionary
    sorted_grouped_devices_dict = {
        item[1]['display']: {
            'devices': item[1]['devices'],
            'total_repair_cost': item[1]['total_repair_cost']
        }
        for item in sorted_grouped_devices_list
    }

    # Filter devices whose end_date is within one week from today
    devices_near_end_date = devices.filter(
        delivery_date__range=(today, today + timedelta(days=7))
    ).order_by('delivery_date')  # Sort by delivery_date in ascending order

    # Pass the data to the template
    return render(request, 'repairs/device_list.html', {
        'grouped_devices': sorted_grouped_devices_dict,
        'today': today,
        'devices_near_end_date': devices_near_end_date,
    })

@login_required
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    return render(request, 'repairs/device_detail.html', {'device': device})

def searched_device(request):
    query = request.GET.get('q')
    devices = Device.objects.none()  # Empty queryset initially

    if query:
        devices = Device.objects.filter(series_id=query)

    return render(request, 'repairs/searched_device.html', {'devices': devices})

@login_required
def device_new(request):
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            # return redirect('device_detail', pk=device.pk)
            return redirect('device_list')
    else:
        form = DeviceForm()
    return render(request, 'repairs/device_new.html', {'form': form})

@login_required
def device_edit(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            device = form.save()
            return redirect('device_detail', pk=device.pk)
    else:
        form = DeviceForm(instance=device)
    return render(request, 'repairs/device_edit.html', {'form': form})

# Delete
@login_required
def delete_device(request, pk):
    device = Device.objects.get(pk=pk)
    device.delete()
    return redirect('device_list')

# User
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('device_list')
        else:
            messages.error(request, 'Username or password is incorrect')
    return render(request, 'account/login.html')

def user_logout(request):
    logout(request)
    return redirect('device_list')

def custom_404(request, exception):
    return render(request, '404.html', status=404)