from django.shortcuts import render, get_object_or_404, redirect
from .models import Device
from .forms import DeviceForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def device_list(request):
    devices = Device.objects.all()
    return render(request, 'repairs/device_list.html', {'devices': devices})

def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    return render(request, 'repairs/device_detail.html', {'device': device})

def device_new(request):
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            return redirect('device_detail', pk=device.pk)
    else:
        form = DeviceForm()
    return render(request, 'repairs/device_edit.html', {'form': form})

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