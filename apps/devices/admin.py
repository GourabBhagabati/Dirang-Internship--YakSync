from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'name', 'device_type', 'status', 'battery_level', 'assigned_animal', 'last_communication']
    list_filter = ['device_type', 'status', 'created_at']
    search_fields = ['device_id', 'name', 'installation_location']
    readonly_fields = ['registration_date', 'created_at', 'updated_at']
    fieldsets = (
        ('Device Information', {
            'fields': ('device_id', 'name', 'device_type', 'installation_location')
        }),
        ('Status', {
            'fields': ('status', 'battery_level', 'last_communication')
        }),
        ('Assignment', {
            'fields': ('assigned_animal',)
        }),
        ('Metadata', {
            'fields': ('registration_date', 'created_at', 'updated_at')
        }),
    )
