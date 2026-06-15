from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'severity', 'status', 'animal', 'device', 'timestamp', 'resolved_by']
    list_filter = ['alert_type', 'severity', 'status', 'timestamp']
    search_fields = ['title', 'description', 'animal__animal_id', 'animal__name', 'device__device_id']
    readonly_fields = ['timestamp', 'acknowledged_at', 'resolved_at']
    date_hierarchy = 'timestamp'
    fieldsets = (
        ('Alert Information', {
            'fields': ('title', 'alert_type', 'severity', 'description')
        }),
        ('IoT Entities', {
            'fields': ('animal', 'device', 'sensor_reading')
        }),
        ('Legacy Entity Tracking', {
            'classes': ('collapse',),
            'fields': ('related_entity_type', 'related_entity_id')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'timestamp', 'acknowledged_at', 'acknowledged_by', 'resolved_at', 'resolved_by')
        }),
    )

