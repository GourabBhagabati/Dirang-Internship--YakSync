from django.db import models
from django.contrib.auth.models import User
from apps.animals.models import Animal


class TreatmentProtocol(models.Model):
    """Treatment protocol definitions"""
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    duration_days = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='protocols_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'treatment_protocols'
        ordering = ['-created_at']
        verbose_name = 'Treatment Protocol'
        verbose_name_plural = 'Treatment Protocols'
    
    def __str__(self):
        return self.name


class ProtocolStep(models.Model):
    """Individual steps within a treatment protocol"""
    
    protocol = models.ForeignKey(TreatmentProtocol, on_delete=models.CASCADE, related_name='steps')
    step_number = models.IntegerField()
    description = models.TextField()
    hormone_type = models.CharField(max_length=100)
    dosage = models.DecimalField(max_digits=10, decimal_places=2)
    day_offset = models.IntegerField()  # Days from protocol start
    time_of_day = models.TimeField()
    
    class Meta:
        db_table = 'protocol_steps'
        ordering = ['protocol', 'step_number']
        verbose_name = 'Protocol Step'
        verbose_name_plural = 'Protocol Steps'
        unique_together = ['protocol', 'step_number']
    
    def __str__(self):
        return f"{self.protocol.name} - Step {self.step_number}"


class TreatmentAssignment(models.Model):
    """Assignment of protocols to animals"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    protocol = models.ForeignKey(TreatmentProtocol, on_delete=models.CASCADE, related_name='assignments')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='treatment_assignments')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)  # Percentage 0-100
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assignments_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'treatment_assignments'
        ordering = ['-created_at']
        verbose_name = 'Treatment Assignment'
        verbose_name_plural = 'Treatment Assignments'
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return f"{self.protocol.name} → {self.animal.animal_id}"
