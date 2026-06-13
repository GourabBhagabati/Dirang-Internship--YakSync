from django.contrib import admin
from .models import Animal


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['animal_id', 'name', 'species', 'breed', 'gender', 'age', 'health_status', 'reproductive_status', 'created_at']
    list_filter = ['species', 'gender', 'health_status', 'reproductive_status', 'created_at']
    search_fields = ['animal_id', 'name', 'species', 'breed']
    readonly_fields = ['registration_date', 'created_at', 'updated_at']
    fieldsets = (
        ('Identification', {
            'fields': ('animal_id', 'name', 'species', 'breed')
        }),
        ('Physical Attributes', {
            'fields': ('age', 'gender', 'weight')
        }),
        ('Health & Reproductive', {
            'fields': ('health_status', 'reproductive_status')
        }),
        ('Metadata', {
            'fields': ('created_by', 'registration_date', 'created_at', 'updated_at')
        }),
    )
