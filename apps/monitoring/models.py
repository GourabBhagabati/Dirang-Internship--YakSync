from django.db import models
from apps.devices.models import Device
from apps.animals.models import Animal


class SensorReading(models.Model):
    """Sensor data readings from IoT devices"""
    
    SENSOR_TYPE_CHOICES = [
        ('temperature', 'Body Temperature'),
        ('movement', 'Movement Level'),
        ('reproductive_indicator', 'Reproductive Indicator'),
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='sensor_readings')
    sensor_type = models.CharField(max_length=50, choices=SENSOR_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=4)
    unit = models.CharField(max_length=20)  # celsius, steps, indicator_level
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    is_abnormal = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'sensor_readings'
        ordering = ['-timestamp']
        verbose_name = 'Sensor Reading'
        verbose_name_plural = 'Sensor Readings'
        indexes = [
            models.Index(fields=['animal', 'sensor_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.sensor_type} - {self.animal.animal_id} @ {self.timestamp}"
