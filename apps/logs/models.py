from django.db import models
from django.contrib.auth.models import User

class ActivityLog(models.Model):
    """User activity and system event logging"""
    
    ACTION_TYPE_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('generate_report', 'Generate Report'),
        ('download_pdf', 'Download PDF'),
        ('alert_action', 'Alert Action'),
    ]
    
    MODULE_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('animals', 'Animals'),
        ('devices', 'Devices'),
        ('monitoring', 'Monitoring'),
        ('hormones', 'Hormones'),
        ('protocols', 'Protocols'),
        ('alerts', 'Alerts'),
        ('reports', 'Reports'),
        ('profile', 'Profile'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    user_role = models.CharField(max_length=50, blank=True, null=True)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    module_accessed = models.CharField(max_length=50, choices=MODULE_CHOICES, blank=True, null=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Backward compatibility fields
    entity_type = models.CharField(max_length=50, blank=True, null=True)
    entity_id = models.IntegerField(null=True, blank=True)
    
    # Session tracking fields
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    session_duration = models.DurationField(null=True, blank=True)
    
    class Meta:
        db_table = 'activity_logs'
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
            models.Index(fields=['module_accessed', '-timestamp']),
        ]
        
    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{user_str} - {self.get_action_type_display()} - {self.timestamp}"
