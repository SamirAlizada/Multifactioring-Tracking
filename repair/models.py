from django.db import models
from dateutil.relativedelta import relativedelta
from django.utils import timezone

class Device(models.Model):
    STATUS_CHOICES = [
        ('Received', 'Received'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Delivered', 'Delivered')
    ]

    device_name = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=100)
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2)
    repair_duration = models.IntegerField()
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
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.device_name} - {self.customer_name}"