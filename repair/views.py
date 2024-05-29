from django.shortcuts import render, get_object_or_404, redirect
from .models import Device, Product, ProductSold
from .forms import DeviceForm, ProductForm, ProductSoldForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import datetime, date, timedelta
import logging
from django.contrib.auth.decorators import login_required

#Add
@login_required
def add_device(request):
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            # return redirect('device_detail', pk=device.pk)
            return redirect('device_list')
    else:
        form = DeviceForm()
    return render(request, 'repairs/add_device.html', {'form': form})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('add_product') 
    else:
        form = ProductForm()
    return render(request, 'product/add_product.html', {'form': form})

def add_product_sold(request):
    if request.method == 'POST':
        form = ProductSoldForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product sold added successfully!')
            return redirect('add_product_sold')
    else:
        form = ProductSoldForm()
    return render(request, 'productSold/add_product_sold.html', {'form': form})
#------------------------------------------------------------------------------

#Lists
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

def product_list(request):
    products = Product.objects.all()

    query = request.GET.get('q')
    if query:
        products = products.filter(product_name__icontains=query)

    return render(request, 'product/product_list.html', {'products': products})

def product_sold_list(request):
    today = date.today()

    # Retrieve the search query
    query = request.GET.get('q')

    # Get all product_solds or filter based on the search query
    product_solds = ProductSold.objects.all()
    
    if query:
        product_solds = product_solds.filter(product_name__name__icontains=query)

    # Create a dictionary for grouping product_solds by month
    grouped_product_solds_dict = {}
    for product_sold in product_solds:
        # Extract month and year from `date`
        month_key = product_sold.date.strftime('%Y-%m')
        month_display = product_sold.date.strftime('%B %Y')

        # Calculate the sale amount for the product_sold
        sale_amount = product_sold.count * product_sold.price

        # Group product_solds by year-month key
        if month_key not in grouped_product_solds_dict:
            grouped_product_solds_dict[month_key] = {
                'display': month_display,
                'product_solds': [],
                'total_sales': 0  # Initialize total monthly sales
            }

        # Add the product_sold to the corresponding month's group
        grouped_product_solds_dict[month_key]['product_solds'].append(product_sold)

        # Add the product_sold's sale amount to the total sales for the month
        grouped_product_solds_dict[month_key]['total_sales'] += sale_amount

    # Convert the dictionary to a list of tuples for sorting
    sorted_grouped_product_solds_list = sorted(
        grouped_product_solds_dict.items(),
        key=lambda x: x[0],
        reverse=True
    )

    # Convert the sorted list back to a dictionary
    sorted_grouped_product_solds_dict = {
        item[1]['display']: {
            'product_solds': item[1]['product_solds'],
            'total_sales': item[1]['total_sales']
        }
        for item in sorted_grouped_product_solds_list
    }

    # Pass the `grouped_product_solds` data to the `product_sold_list.html` template
    return render(request, 'productSold/product_sold_list.html', {
        'grouped_product_solds': sorted_grouped_product_solds_dict,
        'today': today,
    })
#------------------------------------------------------------------------------

#Updates
@login_required
def update_device(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            device = form.save()
            return redirect('device_detail', pk=device.pk)
    else:
        form = DeviceForm(instance=device)
    return render(request, 'repairs/update_device.html', {'form': form})

def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_panel')
    return render(request, 'product/update_product.html', {'form': form})

def update_product_sold(request, pk):
    product_sold = get_object_or_404(ProductSold, pk=pk)
    form = ProductSoldForm(instance=product_sold)
    if request.method == 'POST':
        form = ProductSoldForm(request.POST, instance=product_sold)
        if form.is_valid():
            form.save()
            return redirect('product_sold_panel')
    return render(request, 'productSold/update_product_sold.html', {'form': form})
#----------------------------------------------------------------------

#Delete
@login_required
def delete_device(request, pk):
    device = Device.objects.get(pk=pk)
    device.delete()
    return redirect('device_list')

def delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('product/product_panel')

def delete_product_sold(request, pk):
    product_sold = ProductSold.objects.get(pk=pk)
    product_sold.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('productSold/product_sold_panel')

#Panels
def product_panel(request):
    products = Product.objects.all()

    query = request.GET.get('q')
    if query:
        products = products.filter(product_name__icontains=query)

    return render(request, 'product/product_panel.html', {'products': products})

def product_sold_panel(request):
    today = date.today()

    # Retrieve the search query
    query = request.GET.get('q')

    # Get all product_solds or filter based on the search query
    product_solds = ProductSold.objects.all()
    
    if query:
        product_solds = product_solds.filter(product_name__name__icontains=query)

    # Create a dictionary for grouping product_solds by month
    grouped_product_solds_dict = {}
    for product_sold in product_solds:
        # Extract month and year from `date`
        month_key = product_sold.date.strftime('%Y-%m')
        month_display = product_sold.date.strftime('%B %Y')

        # Calculate the sale amount for the product_sold
        sale_amount = product_sold.count * product_sold.price

        # Group product_solds by year-month key
        if month_key not in grouped_product_solds_dict:
            grouped_product_solds_dict[month_key] = {
                'display': month_display,
                'product_solds': [],
                'total_sales': 0  # Initialize total monthly sales
            }

        # Add the product_sold to the corresponding month's group
        grouped_product_solds_dict[month_key]['product_solds'].append(product_sold)

        # Add the product_sold's sale amount to the total sales for the month
        grouped_product_solds_dict[month_key]['total_sales'] += sale_amount

    # Convert the dictionary to a list of tuples for sorting
    sorted_grouped_product_solds_list = sorted(
        grouped_product_solds_dict.items(),
        key=lambda x: x[0],
        reverse=True
    )

    # Convert the sorted list back to a dictionary
    sorted_grouped_product_solds_dict = {
        item[1]['display']: {
            'product_solds': item[1]['product_solds'],
            'total_sales': item[1]['total_sales']
        }
        for item in sorted_grouped_product_solds_list
    }

    # Pass the `grouped_product_solds` data to the `product_sold_list.html` template
    return render(request, 'productSold/product_sold_panel.html', {
        'grouped_product_solds': sorted_grouped_product_solds_dict,
        'today': today,
    })
#------------------------------------------------------------------------------

# Operations
def increase_stock(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.stock_number += 1
    product.save()
    return redirect('product_panel')

def decrease_stock(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    # to check before reducing stock_number
    # you can add any stock control (for example, negative value prevention).
    if product.stock_number > 0:
        product.stock_number -= 1
        product.save()
    return redirect('product_panel')

def increase_sold(request, pk):
    product_sold = get_object_or_404(ProductSold, pk=pk)
    product_sold.count += 1
    product_sold.save()
    return redirect('product_sold_panel')

def decrease_sold(request, pk):
    product_sold = get_object_or_404(ProductSold, pk=pk)
    # to check before reducing count
    # you can add any count control (for example, negative value prevention).
    if product_sold.count > 0:
        product_sold.count -= 1
        product_sold.save()
    return redirect('product_sold_panel')
#-----------------------------------------------------------------------------

#Details
@login_required
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    return render(request, 'repairs/device_detail.html', {'device': device})
#-----------------------------------------------------------------------------

#Seach the product by Series ID
def searched_device(request):
    query = request.GET.get('q')
    devices = Device.objects.none()  # Empty queryset initially

    if query:
        devices = Device.objects.filter(series_id=query)

    return render(request, 'repairs/searched_device.html', {'devices': devices})
#-----------------------------------------------------------------------------

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
#-----------------------------------------------------------------------------

#404
def custom_404(request, exception):
    return render(request, '404.html', status=404)
#-----------------------------------------------------------------------------