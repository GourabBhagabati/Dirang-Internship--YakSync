from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile for YakSync users"""
    
    ROLE_CHOICES = [
        ('farm_operator', 'Farm Operator'),
        ('veterinarian', 'Veterinarian'),
        ('administrator', 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
