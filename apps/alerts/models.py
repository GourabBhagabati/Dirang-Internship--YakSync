from django.db import models
from django.contrib.auth.models import User


class Alert(models.Model):
    """System alerts for critical conditions"""
    
    ALERT_TYPE_CHOICES = [
        ('low_hormone', 'Low Hormone Level'),
        ('device_disconnection', 'Device Disconnection'),
        ('low_battery', 'Low Battery'),
        ('abnormal_reading', 'Abnormal Reading'),
        ('missed_schedule', 'Missed Schedule'),
    ]
    
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
    ]
    
    title = models.CharField(max_length=200)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField()
    related_entity_type = models.CharField(max_length=50)  # animal, device, reservoir, protocol
    related_entity_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts_resolved')
    
    class Meta:
        db_table = 'alerts'
        ordering = ['-timestamp']
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'
        indexes = [
            models.Index(fields=['status', '-timestamp']),
            models.Index(fields=['alert_type', 'severity']),
        ]
    
    def __str__(self):
        return f"{self.get_severity_display()} - {self.title}"
