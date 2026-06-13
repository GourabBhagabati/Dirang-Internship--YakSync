from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'entity_type', 'entity_id', 'timestamp', 'ip_address']
    list_filter = ['action_type', 'entity_type', 'timestamp']
    search_fields = ['user__username', 'description', 'entity_type']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
