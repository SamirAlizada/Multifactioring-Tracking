from django.db import models

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
    delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Received')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.device_name} - {self.customer_name}"