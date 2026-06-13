from django.contrib import admin
from .models import TreatmentProtocol, ProtocolStep, TreatmentAssignment


class ProtocolStepInline(admin.TabularInline):
    model = ProtocolStep
    extra = 1


@admin.register(TreatmentProtocol)
class TreatmentProtocolAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_days', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProtocolStepInline]


@admin.register(TreatmentAssignment)
class TreatmentAssignmentAdmin(admin.ModelAdmin):
    list_display = ['protocol', 'animal', 'status', 'progress', 'start_date', 'end_date', 'assigned_by']
    list_filter = ['status', 'start_date', 'created_at']
    search_fields = ['protocol__name', 'animal__animal_id', 'animal__name']
    readonly_fields = ['created_at', 'updated_at']
