from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile for YakSync users"""
    
    ROLE_CHOICES = [
        ('veterinarian', 'Veterinarian'),
        ('farm_operator', 'Farm Operator'),
        ('researcher', 'Researcher'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
