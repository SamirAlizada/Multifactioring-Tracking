from django.db import models
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import random
import string

def generate_series_id():
    letters = random.choices(string.ascii_uppercase, k=3)
    digits = random.choices(string.digits, k=3)
    series_id_list = letters + digits
    random.shuffle(series_id_list)
    return ''.join(series_id_list)

class Device(models.Model):
    STATUS_CHOICES = [
        ('Received', 'Received'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Delivered', 'Delivered')
    ]

    series_id = models.CharField(max_length=6, unique=True, blank=True)  # Make sure this is unique
    device_name = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=100)
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2)
    repair_duration = models.PositiveIntegerField()
    add_date = models.DateField(default=timezone.now)
    delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Received')
    notes = models.TextField(blank=True, null=True)

    def calculate_end_date(self):
        if self.add_date and self.repair_duration:
            self.delivery_date = self.add_date + relativedelta(days=self.repair_duration)

    def save(self, *args, **kwargs):
        # Calculate the payment before saving
        self.calculate_end_date()
        if not self.pk:  # Only for new objects
            self.series_id = generate_series_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.device_name} - {self.customer_name}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self) -> str:
        return f"{self.name}"

class Product(models.Model):
    category_name = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=100)
    price = models.FloatField()
    stock_number = models.PositiveIntegerField()
    date = models.DateField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.product_name}"
    
class ProductSold(models.Model):
    product_name = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    price = models.FloatField()
    count = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.product_name}"

    def save(self, *args, **kwargs):
        if self.pk:
            # # Get the old count value if this row does not create a resale
            previous = ProductSold.objects.get(pk=self.pk)
            difference = self.count - previous.count
        else:
            # New for sale
            difference = self.count
        
        # Update product stock
        product = self.product_name
        product.stock_number -= difference
        product.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        product = self.product_name
        product.stock_number += self.count
        product.save()
        
        super().delete(*args, **kwargs)