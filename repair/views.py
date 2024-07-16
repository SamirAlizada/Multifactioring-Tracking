from django.shortcuts import render, get_object_or_404, redirect
from .models import Device, Product, ProductSold, Category
from .forms import DeviceForm, ProductForm, ProductSoldForm, CategoryForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.utils.timezone import now

#Add
@login_required
def add_device(request):
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('device_list')
    else:
        form = DeviceForm()
    return render(request, 'repairs/add_device.html', {'form': form})

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('add_category') 
    else:
        form = CategoryForm()
    return render(request, 'category/add_category.html', {'form': form})

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
            messages.error(request, 'As many products as you entered are out of stock.')
    else:
        form = ProductSoldForm()
    return render(request, 'productSold/add_product_sold.html', {'form': form})

def load_products(request):
    category_id = request.GET.get('category_id')
    products = Product.objects.filter(category_name_id=category_id).order_by('product_name')
    return JsonResponse(list(products.values('id', 'product_name')), safe=False)

#------------------------------------------------------------------------------

#Lists

# List of month names in Azerbaijani
months_en = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

def device_list(request):
    today = date.today()

    # Retrieve the search query
    query = request.GET.get('q')

    # Get all devices or filter based on the search query
    devices = Device.objects.all()
    if query:
        devices = devices.filter(device_name__icontains=query)

    # Get the earliest year from the Device data
    if Device.objects.exists():
        first_device_year = Device.objects.earliest('add_date').add_date.year
    else:
        first_device_year = today.year

    start_year = first_device_year
    current_year = today.year

    # Generate years from the earliest year to the current year
    years = range(start_year, current_year + 1)

    # Generate months
    months = [
        {'value': 1, 'name': 'January'},
        {'value': 2, 'name': 'February'},
        {'value': 3, 'name': 'March'},
        {'value': 4, 'name': 'April'},
        {'value': 5, 'name': 'May'},
        {'value': 6, 'name': 'June'},
        {'value': 7, 'name': 'July'},
        {'value': 8, 'name': 'August'},
        {'value': 9, 'name': 'September'},
        {'value': 10, 'name': 'October'},
        {'value': 11, 'name': 'November'},
        {'value': 12, 'name': 'December'},
    ]

    # Get selected year and month from GET parameters or use current values
    selected_year = int(request.GET.get('year', current_year))
    selected_month = int(request.GET.get('month', today.month))

    # Filter devices by selected year and month
    devices = devices.filter(add_date__year=selected_year, add_date__month=selected_month)

    # Dictionary to group devices by month
    grouped_devices_dict = {}

    # Grouping devices by month key and calculating total repair costs
    for device in devices:
        # Create month and year key from the registration date
        month_key = device.add_date.strftime('%Y-%m')
        
        # Extract year and month from the add_date
        year = device.add_date.year
        month = device.add_date.month
        
        # Use months list for month name
        month_display = f"{months_en[month - 1]} {year}"

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

    # Filter devices whose delivery_date is within one week from today
    devices_near_end_date = devices.filter(
        delivery_date__range=(today, today + timedelta(days=7))
    ).order_by('delivery_date')  # Sort by delivery_date in ascending order

    # Pass the data to the template
    context = {
        'grouped_devices': sorted_grouped_devices_dict,
        'today': today,
        'devices_near_end_date': devices_near_end_date,
        'years': years,
        'months': months,
        'selected_year': selected_year,
        'selected_month': selected_month,
    }
    return render(request, 'repairs/device_list.html', context)

def product_list(request):
    # Get all categories
    categories = Category.objects.all()

    # Get all products or filter by selected category
    products = Product.objects.all()

    # Retrieve the search query
    query = request.GET.get('q')
    if query:
        products = products.filter(product_name__icontains=query)

    # Retrieve the selected category from the query parameters
    selected_category_id = request.GET.get('category')
    if selected_category_id:
        try:
            selected_category_id = int(selected_category_id)
            products = products.filter(category_name_id=selected_category_id)
        except ValueError:
            # Handle invalid category id
            selected_category_id = None

    products = products.order_by("stock_number")

    return render(request, 'product/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category_id': selected_category_id
    })

def product_sold_list(request):
    today = date.today()

    # Retrieve the search query
    query = request.GET.get('q')

    # Get all product_solds or filter based on the search query
    product_solds = ProductSold.objects.all()
    # if query:
    #     product_solds = product_solds.filter(product_name__name__icontains=query)

    # Get the earliest year from the ProductSold data
    if ProductSold.objects.exists():
        first_product_sold_year = ProductSold.objects.earliest('date').date.year
    else:
        first_product_sold_year = today.year

    if Product.objects.exists():
        first_product_year = Product.objects.earliest('date').date.year
    else:
        first_product_year = today.year

    start_year = min(first_product_year, first_product_sold_year)

    # Generate years from the earliest year to the current year
    current_year = today.year
    years = range(start_year, current_year + 1)

    # Generate months
    months = [
        {'value': 1, 'name': 'January'},
        {'value': 2, 'name': 'February'},
        {'value': 3, 'name': 'March'},
        {'value': 4, 'name': 'April'},
        {'value': 5, 'name': 'May'},
        {'value': 6, 'name': 'June'},
        {'value': 7, 'name': 'July'},
        {'value': 8, 'name': 'August'},
        {'value': 9, 'name': 'September'},
        {'value': 10, 'name': 'October'},
        {'value': 11, 'name': 'November'},
        {'value': 12, 'name': 'December'},
    ]

    # Get selected year and month from GET parameters or use current values
    selected_year = int(request.GET.get('year', current_year))
    selected_month = int(request.GET.get('month', today.month))

    # Filter product_solds by selected year and month
    product_solds = product_solds.filter(date__year=selected_year, date__month=selected_month)

    # Create a dictionary for grouping product_solds by month
    grouped_product_solds_dict = {}
    for product_sold in product_solds:
        # Extract month and year from `date`
        month_key = product_sold.date.strftime('%Y-%m')
        month_display = product_sold.date.strftime('%B %Y')

        # Calculate the sale amount for the product_sold
        sale_amount = product_sold.count * product_sold.price
        product_sold.total_price = sale_amount  # Add total_price attribute to each product_sold

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

    # Pass the `grouped_product_solds` data to the template
    context = {
        'grouped_product_solds': sorted_grouped_product_solds_dict,
        'today': today,
        'years': years,
        'months': months,
        'selected_year': selected_year,
        'selected_month': selected_month,
    }
    return render(request, 'productSold/product_sold_list.html', context)

#------------------------------------------------------------------------------

#Updates
@login_required
def update_device(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return redirect('device_list')
    else:
        form = DeviceForm(instance=device)
    return render(request, 'repairs/update_device.html', {'form': form})

def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(instance=category)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_panel')
    return render(request, 'category/update_category.html', {'form': form})

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
    if request.method == 'POST':
        form = ProductSoldForm(request.POST, instance=product_sold)
        if form.is_valid():
            form.save()
            return redirect('product_sold_panel')
    else:
        form = ProductSoldForm(instance=product_sold)
    return render(request, 'productSold/update_product_sold.html', {'form': form})

#----------------------------------------------------------------------

#Delete
@login_required
def delete_device(request, pk):
    device = Device.objects.get(pk=pk)
    device.delete()
    return redirect('device_list')

def delete_category(request, pk):
    category = Category.objects.get(pk=pk)
    category.delete()
    return redirect('category_panel')

def delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()
    # messages.success(request, 'Product deleted successfully!')
    return redirect('product_panel')

def delete_product_sold(request, pk):
    product_sold = ProductSold.objects.get(pk=pk)
    product_sold.delete()
    # messages.success(request, 'Product deleted successfully!')
    return redirect('product_sold_panel')

#Panels
def category_panel(request):
    categories = Category.objects.all()

    query = request.GET.get('q')
    if query:
        categories = categories.filter(name__icontains=query)

    return render(request, 'category/category_panel.html', {'categories': categories})

def product_panel(request):
    # Get all categories
    categories = Category.objects.all()

    # Get all products or filter by selected category
    products = Product.objects.all()

    # Retrieve the search query
    query = request.GET.get('q')
    if query:
        products = products.filter(product_name__icontains=query)

    # Retrieve the selected category from the query parameters
    selected_category_id = request.GET.get('category')
    if selected_category_id:
        try:
            selected_category_id = int(selected_category_id)
            products = products.filter(category_name_id=selected_category_id)
        except ValueError:
            # Handle invalid category id
            selected_category_id = None

    products = products.order_by("stock_number")

    return render(request, 'product/product_panel.html', {
        'products': products,
        'categories': categories,
        'selected_category_id': selected_category_id
    })

def product_sold_panel(request):
    today = date.today()

    # Retrieve the search query
    query = request.GET.get('q')

    # Get all product_solds or filter based on the search query
    product_solds = ProductSold.objects.all()
    # if query:
    #     product_solds = product_solds.filter(product_name__name__icontains=query)

    # Get selected year and month from GET parameters or use current values
    current_year = today.year
    current_month = today.month
    selected_year = int(request.GET.get('year', current_year))
    selected_month = int(request.GET.get('month', current_month))

    # Filter product_solds by selected year and month
    product_solds = product_solds.filter(date__year=selected_year, date__month=selected_month)

    # Create a dictionary for grouping product_solds by month
    grouped_product_solds_dict = {}
    for product_sold in product_solds:
        # Extract month and year from `date`
        month_key = product_sold.date.strftime('%Y-%m')
        month_display = product_sold.date.strftime('%B %Y')

        # Calculate the sale amount for the product_sold
        sale_amount = product_sold.count * product_sold.price
        product_sold.total_price = sale_amount  # Add total_price attribute to each product_sold

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

    # Generate years and months for dropdowns
    years = range(2020, current_year + 1)
    months = [
        {'value': 1, 'name': 'January'},
        {'value': 2, 'name': 'February'},
        {'value': 3, 'name': 'March'},
        {'value': 4, 'name': 'April'},
        {'value': 5, 'name': 'May'},
        {'value': 6, 'name': 'June'},
        {'value': 7, 'name': 'July'},
        {'value': 8, 'name': 'August'},
        {'value': 9, 'name': 'September'},
        {'value': 10, 'name': 'October'},
        {'value': 11, 'name': 'November'},
        {'value': 12, 'name': 'December'},
    ]

    # Pass the `grouped_product_solds` data to the template
    context = {
        'grouped_product_solds': sorted_grouped_product_solds_dict,
        'today': today,
        'years': years,
        'months': months,
        'selected_year': selected_year,
        'selected_month': selected_month,
    }
    return render(request, 'productSold/product_sold_panel.html', context)
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
    product = product_sold.product_name
    
    if product.stock_number > 0:
        product_sold.count += 1
        product_sold.save()
        product.save()
        messages.success(request, 'Product sold count increased successfully!')
    else:
        messages.error(request, 'No more stock available.')

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
    return redirect('searched_device')
#-----------------------------------------------------------------------------

#404
def custom_404(request, exception):
    return render(request, '404.html', status=404)
#-----------------------------------------------------------------------------

def device_monthly_repair_costs(selected_year):
    monthly_repair_costs_data = (
        Device.objects.filter(add_date__year=selected_year)
        .annotate(month=Cast('add_date__month', FloatField()))
        .values('month')
        .annotate(total_repair_cost=Sum('repair_cost', output_field=FloatField()))
        .order_by('month')
    )

    device_labels = [date(1900, int(entry['month']), 1).strftime('%B') for entry in monthly_repair_costs_data]
    total_repair_costs = [entry['total_repair_cost'] for entry in monthly_repair_costs_data]

    return device_labels, total_repair_costs


def sales_chart(request):
    # Get all years from the data
    years = ProductSold.objects.dates('date', 'year')
    years = [year.year for year in years]

    # Get selected year from the request or use the current year
    selected_year = request.GET.get('year', date.today().year)

    # Get sales data for the selected year, grouped by month
    sales_data = (
        ProductSold.objects.filter(date__year=selected_year)
        .annotate(month=Cast('date__month', FloatField()))
        .values('month')
        .annotate(total_sales=Sum(F('count') * F('price'), output_field=FloatField()))
        .order_by('month')
    )

    # Prepare data for Chart.js
    labels = [date(1900, int(entry['month']), 1).strftime('%B') for entry in sales_data]
    total_sales = [entry['total_sales'] for entry in sales_data]

    context = {
        "years": years,
        "selected_year": int(selected_year),
        "labels": labels,
        "total_sales": total_sales,
    }

    return context

def price_comparison_chart(request):
    # Get the current year
    current_year = date.today().year

    # Get the earliest year from the Product and ProductSold data
    first_product_year = Product.objects.earliest('date').date.year if Product.objects.exists() else current_year
    first_product_sold_year = ProductSold.objects.earliest('date').date.year if ProductSold.objects.exists() else current_year
    start_year = min(first_product_year, first_product_sold_year)

    # Get all years from the data starting from the earliest year
    years = range(start_year, current_year + 1)

    months = [
        {'value': 1, 'name': 'Yanvar'},
        {'value': 2, 'name': 'Fevral'},
        {'value': 3, 'name': 'Mart'},
        {'value': 4, 'name': 'Aprel'},
        {'value': 5, 'name': 'May'},
        {'value': 6, 'name': 'İyun'},
        {'value': 7, 'name': 'İyul'},
        {'value': 8, 'name': 'Avqust'},
        {'value': 9, 'name': 'Sentyabr'},
        {'value': 10, 'name': 'Oktyabr'},
        {'value': 11, 'name': 'Noyabr'},
        {'value': 12, 'name': 'Dekabr'},
    ]

    # Get selected year and month from the request or use the current year and month
    selected_year = int(request.GET.get('year', current_year))
    selected_month = int(request.GET.get('month', date.today().month))
    
    # Get the device repair costs for the selected year
    device_labels, monthly_repair_costs = device_monthly_repair_costs(selected_year)

    # Get the repair cost for the selected month
    selected_month_repair_cost = monthly_repair_costs[selected_month - 1] if selected_month <= len(monthly_repair_costs) else 0

    # Calculate the total cost (Product prices * stock_number) for the selected month and year
    total_cost = sum(product.price * product.stock_number for product in Product.objects.filter(date__year=selected_year, date__month=selected_month))

    # Calculate the total income (ProductSold prices * count) for the selected month and year
    total_income = sum(product_sold.price * product_sold.count for product_sold in ProductSold.objects.filter(date__year=selected_year, date__month=selected_month)) + selected_month_repair_cost

    # Calculate the total price difference including repair costs
    total_price_difference = total_income - total_cost

    context = {
        "years": years,
        "months": months,
        "selected_year": selected_year,
        "selected_month": selected_month,
        "total_cost": total_cost,
        "total_income": total_income,
        "total_price_difference": total_price_difference,
        "selected_month_repair_cost": selected_month_repair_cost,
    }

    return context

def combined_charts_view(request):
    sales_context = sales_chart(request)
    price_comparison_context = price_comparison_chart(request)

    # Get the current year for device monthly repair costs
    selected_year = int(request.GET.get('year', date.today().year))
    device_labels, total_repair_costs = device_monthly_repair_costs(selected_year)

    context = {
        **sales_context,
        **price_comparison_context,
        "device_labels": device_labels,
        "total_repair_costs": total_repair_costs,
    }

    return render(request, 'chart/combined_charts.html', context)

def daily_report(request):
    current_date = now().date()
    selected_date_str = request.GET.get('date', current_date.strftime('%Y-%m-%d'))
    
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = current_date
    
    added_devices = Device.objects.filter(add_date=selected_date)
    delivery_devices = Device.objects.filter(delivery_date=selected_date)
    sold_products = ProductSold.objects.filter(date=selected_date)
    
    context = {
        'current_date': current_date,
        'selected_date': selected_date,
        'added_devices': added_devices,
        'delivery_devices': delivery_devices,
        'sold_products': sold_products,
    }
    
    return render(request, 'daily_report.html', context)