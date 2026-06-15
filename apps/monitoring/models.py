from django.db import models
from apps.devices.models import Device
from apps.animals.models import Animal


class SensorReading(models.Model):
    """Sensor data readings from IoT devices"""
    
    SENSOR_TYPE_CHOICES = [
        ('temperature', 'Body Temperature'),
        ('movement', 'Movement Level'),
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
    
    def save(self, *args, **kwargs):
        is_abnormal = False
        alert_title = None
        alert_severity = None
        alert_desc = None
        alert_type = None

        # Determine thresholds
        if self.sensor_type == 'temperature':
            if self.value > 39.5:
                is_abnormal = True
                alert_title = f"High Temperature Alert for {self.animal.animal_id}"
                alert_severity = 'critical'
                alert_desc = f"Yak {self.animal.name} ({self.animal.animal_id}) registered high body temperature of {self.value}°C (threshold: > 39.5°C)."
                alert_type = 'temperature'
            elif self.value < 37.5:
                is_abnormal = True
                alert_title = f"Low Temperature Alert for {self.animal.animal_id}"
                alert_severity = 'warning'
                alert_desc = f"Yak {self.animal.name} ({self.animal.animal_id}) registered low body temperature of {self.value}°C (threshold: < 37.5°C)."
                alert_type = 'temperature'
        elif self.sensor_type == 'movement':
            if self.value == 0:
                is_abnormal = True
                alert_title = f"No Movement Alert for {self.animal.animal_id}"
                alert_severity = 'critical'
                alert_desc = f"Yak {self.animal.name} ({self.animal.animal_id}) registered no movement (value: 0 steps)."
                alert_type = 'movement'
            elif self.value < 100:
                is_abnormal = True
                alert_title = f"Low Movement Alert for {self.animal.animal_id}"
                alert_severity = 'warning'
                alert_desc = f"Yak {self.animal.name} ({self.animal.animal_id}) registered low movement of {self.value} steps (threshold: < 100 steps)."
                alert_type = 'movement'
            elif self.value > 10000:
                is_abnormal = True
                alert_title = f"Excessive Movement Alert for {self.animal.animal_id}"
                alert_severity = 'warning'
                alert_desc = f"Yak {self.animal.name} ({self.animal.animal_id}) registered excessive movement of {self.value} steps (threshold: > 10000 steps)."
                alert_type = 'movement'

        # If it was already marked abnormal or resolved by rules as abnormal:
        if self.is_abnormal or is_abnormal:
            self.is_abnormal = True

        super().save(*args, **kwargs)

        # Only create alert if triggered by threshold rules
        if is_abnormal:
            from apps.alerts.models import Alert
            Alert.objects.create(
                title=alert_title,
                alert_type=alert_type,
                severity=alert_severity,
                description=alert_desc,
                related_entity_type='animal',
                related_entity_id=self.animal.id,
                animal=self.animal,
                device=self.device,
                sensor_reading=self,
                status='active'
            )

    def __str__(self):
        return f"{self.get_sensor_type_display()} - {self.animal.animal_id} @ {self.timestamp}"
