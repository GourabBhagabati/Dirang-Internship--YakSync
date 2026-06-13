from django.contrib import admin
from .models import SensorReading


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['device', 'animal', 'sensor_type', 'value', 'unit', 'is_abnormal', 'timestamp']
    list_filter = ['sensor_type', 'is_abnormal', 'timestamp']
    search_fields = ['device__device_id', 'animal__animal_id', 'animal__name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
