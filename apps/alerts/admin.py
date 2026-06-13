from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'severity', 'status', 'related_entity_type', 'related_entity_id', 'timestamp', 'resolved_by']
    list_filter = ['alert_type', 'severity', 'status', 'timestamp']
    search_fields = ['title', 'description']
    readonly_fields = ['timestamp', 'resolved_at']
    date_hierarchy = 'timestamp'
    fieldsets = (
        ('Alert Information', {
            'fields': ('title', 'alert_type', 'severity', 'description')
        }),
        ('Related Entity', {
            'fields': ('related_entity_type', 'related_entity_id')
        }),
        ('Status', {
            'fields': ('status', 'timestamp', 'resolved_at', 'resolved_by')
        }),
    )
