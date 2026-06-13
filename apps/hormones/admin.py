from django.contrib import admin
from .models import HormoneReservoir, HormoneRelease


@admin.register(HormoneReservoir)
class HormoneReservoirAdmin(admin.ModelAdmin):
    list_display = ['hormone_type', 'current_quantity', 'initial_quantity', 'unit', 'low_threshold', 'is_low', 'created_at']
    list_filter = ['hormone_type', 'created_at']
    search_fields = ['hormone_type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(HormoneRelease)
class HormoneReleaseAdmin(admin.ModelAdmin):
    list_display = ['reservoir', 'animal', 'quantity', 'performed_by', 'timestamp']
    list_filter = ['reservoir__hormone_type', 'timestamp']
    search_fields = ['animal__animal_id', 'animal__name', 'reservoir__hormone_type']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
