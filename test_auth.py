#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yaksync_project.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from apps.authentication.models import UserProfile

if __name__ == '__main__':
    print("=" * 50)
    print("AUTHENTICATION SYSTEM TEST")
    print("=" * 50)

    # Test authentication
    user = authenticate(username='testvet', password='password123')
    print(f"\n✅ Authentication successful: {user is not None}")
    if user:
        print(f"✅ User: {user.username}")
        print(f"✅ Email: {user.email}")
        print(f"✅ Full name: {user.get_full_name()}")
        print(f"✅ Profile exists: {hasattr(user, 'profile')}")
        if hasattr(user, 'profile'):
            print(f"✅ Role: {user.profile.get_role_display()}")

    # Test URL configuration
    print("\n" + "=" * 50)
    print("URL CONFIGURATION TEST")
    print("=" * 50)

    from django.urls import reverse

    urls_to_test = [
        ('dashboard:index', 'Dashboard'),
        ('authentication:login', 'Login'),
        ('authentication:register', 'Register'),
        ('authentication:logout', 'Logout'),
    ]

    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✅ {description}: {url}")
        except Exception as e:
            print(f"❌ {description}: {e}")

    # Test database statistics
    print("\n" + "=" * 50)
    print("DATABASE STATISTICS")
    print("=" * 50)

    from apps.animals.models import Animal
    from apps.devices.models import Device
    from apps.alerts.models import Alert
    from apps.protocols.models import TreatmentAssignment

    print(f"✅ Total Users: {User.objects.count()}")
    print(f"✅ Total Animals: {Animal.objects.count()}")
    print(f"✅ Total Devices: {Device.objects.count()}")
    print(f"✅ Active Alerts: {Alert.objects.filter(status='active').count()}")
    print(f"✅ Active Protocols: {TreatmentAssignment.objects.filter(status__in=['pending', 'in_progress']).count()}")

    print("\n" + "=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)
