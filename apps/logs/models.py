from django.db import models
from django.contrib.auth.models import User


class ActivityLog(models.Model):
    """User activity and system event logging"""
    
    ACTION_TYPE_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    entity_type = models.CharField(max_length=50)  # animal, device, protocol, etc.
    entity_id = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'activity_logs'
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{user_str} - {self.get_action_type_display()} - {self.timestamp}"
