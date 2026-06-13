from django.db import models
from django.contrib.auth.models import User
from apps.animals.models import Animal


class HormoneReservoir(models.Model):
    """Hormone storage containers"""
    
    hormone_type = models.CharField(max_length=100)
    initial_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    current_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)  # ml, mg
    low_threshold = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hormone_reservoirs'
        ordering = ['-created_at']
        verbose_name = 'Hormone Reservoir'
        verbose_name_plural = 'Hormone Reservoirs'
    
    def __str__(self):
        return f"{self.hormone_type} - {self.current_quantity}/{self.initial_quantity} {self.unit}"
    
    @property
    def is_low(self):
        return self.current_quantity <= self.low_threshold


class HormoneRelease(models.Model):
    """Individual hormone release events"""
    
    reservoir = models.ForeignKey(HormoneReservoir, on_delete=models.CASCADE, related_name='releases')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='hormone_releases')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hormone_releases')
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'hormone_releases'
        ordering = ['-timestamp']
        verbose_name = 'Hormone Release'
        verbose_name_plural = 'Hormone Releases'
    
    def __str__(self):
        return f"{self.reservoir.hormone_type} - {self.quantity} to {self.animal.animal_id}"
