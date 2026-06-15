from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_role', 'action_type', 'module_accessed', 'timestamp', 'ip_address', 'session_duration']
    list_filter = ['action_type', 'module_accessed', 'user_role', 'timestamp']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
