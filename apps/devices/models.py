from django.db import models
from apps.animals.models import Animal


class Device(models.Model):
    """IoT devices for monitoring and hormone dispensing"""
    
    DEVICE_TYPE_CHOICES = [
        ('sensor', 'Sensor'),
        ('hormone_dispenser', 'Hormone Dispenser'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]
    
    device_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES)
    installation_location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    battery_level = models.IntegerField(default=100)  # 0-100
    assigned_animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices')
    last_communication = models.DateTimeField(null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'devices'
        ordering = ['-created_at']
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
    
    def __str__(self):
        return f"{self.device_id} - {self.name}"
