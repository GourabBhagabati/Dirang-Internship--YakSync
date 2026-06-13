from django.db import models
from django.contrib.auth.models import User


class Animal(models.Model):
    """Livestock animal records"""
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    HEALTH_STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('sick', 'Sick'),
        ('under_treatment', 'Under Treatment'),
    ]
    
    REPRODUCTIVE_STATUS_CHOICES = [
        ('pregnant', 'Pregnant'),
        ('cycling', 'Cycling'),
        ('not_cycling', 'Not Cycling'),
    ]
    
    animal_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    health_status = models.CharField(max_length=50, choices=HEALTH_STATUS_CHOICES, default='healthy')
    reproductive_status = models.CharField(max_length=50, choices=REPRODUCTIVE_STATUS_CHOICES)
    registration_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='animals_created')
    
    class Meta:
        db_table = 'animals'
        ordering = ['-created_at']
        verbose_name = 'Animal'
        verbose_name_plural = 'Animals'
    
    def __str__(self):
        return f"{self.animal_id} - {self.name}"
