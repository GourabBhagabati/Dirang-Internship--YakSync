from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from apps.authentication.models import UserProfile
from .models import ActivityLog
import datetime


class ActivityLogsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='farm_operator',
            phone_number='1234567890'
        )

    def test_activity_log_fields(self):
        """Test direct creation and attributes of the ActivityLog model"""
        log = ActivityLog.objects.create(
            user=self.user,
            user_role='farm_operator',
            action_type='view',
            module_accessed='animals',
            description='Viewed animal list',
            ip_address='127.0.0.1'
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.user_role, 'farm_operator')
        self.assertEqual(log.action_type, 'view')
        self.assertEqual(log.module_accessed, 'animals')
        self.assertEqual(log.description, 'Viewed animal list')
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertIn('testuser - View -', str(log))


class ActivityLogsAccessControlTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create different role users
        self.admin_user = User.objects.create_user(
            username='admin_user', password='password123', email='admin@example.com'
        )
        UserProfile.objects.create(user=self.admin_user, role='administrator')
        
        self.vet_user = User.objects.create_user(
            username='vet_user', password='password123', email='vet@example.com'
        )
        UserProfile.objects.create(user=self.vet_user, role='veterinarian')
        
        self.operator_user = User.objects.create_user(
            username='op_user', password='password123', email='op@example.com'
        )
        UserProfile.objects.create(user=self.operator_user, role='farm_operator')
        
        self.superuser = User.objects.create_superuser(
            username='superuser', password='password123', email='super@example.com'
        )
        # Note: Superuser has no UserProfile model initially
        
        self.logs_url = reverse('logs:dashboard')

    def test_unauthenticated_user_redirects_to_login(self):
        """Test that unauthenticated users are redirected to login page"""
        response = self.client.get(self.logs_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_veterinarian_access_denied(self):
        """Test that Veterinarian role gets a 403 Access Denied template"""
        self.client.login(username='vet_user', password='password123')
        response = self.client.get(self.logs_url)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/access_denied.html')

    def test_farm_operator_access_denied(self):
        """Test that Farm Operator role gets a 403 Access Denied template"""
        self.client.login(username='op_user', password='password123')
        response = self.client.get(self.logs_url)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'errors/access_denied.html')

    def test_administrator_access_granted(self):
        """Test that Administrator role is successfully granted access"""
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(self.logs_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logs/activity_dashboard.html')

    def test_superuser_access_granted(self):
        """Test that Superuser without a profile is granted access (inherently Administrator)"""
        self.client.login(username='superuser', password='password123')
        response = self.client.get(self.logs_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logs/activity_dashboard.html')


class ActivityLogsSignalsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='signal_user', password='password123'
        )
        UserProfile.objects.create(user=self.user, role='administrator')

    def test_login_logout_signal_creates_logs(self):
        """Test that logging in and logging out creates corresponding ActivityLog entries"""
        # Clear logs that might have been automatically created during setUp/tests
        ActivityLog.objects.all().delete()

        # Perform Login
        login_success = self.client.login(username='signal_user', password='password123')
        self.assertTrue(login_success)
        
        # Check login activity log exists
        login_logs = ActivityLog.objects.filter(action_type='login', user=self.user)
        self.assertEqual(login_logs.count(), 1)
        login_log = login_logs.first()
        self.assertEqual(login_log.user_role, 'administrator')
        self.assertIsNotNone(login_log.login_time)
        self.assertIn('logged in', login_log.description)

        # Perform Logout
        self.client.logout()
        
        # Check logout activity log exists
        logout_logs = ActivityLog.objects.filter(action_type='logout', user=self.user)
        self.assertEqual(logout_logs.count(), 1)
        logout_log = logout_logs.first()
        self.assertEqual(logout_log.user_role, 'administrator')
        self.assertIsNotNone(logout_log.logout_time)
        self.assertIsNotNone(logout_log.session_duration)
        self.assertIn('logged out', logout_log.description)


class ActivityLogsFilteringTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Admin User to access views
        self.admin = User.objects.create_user(
            username='admin_filter', password='password123'
        )
        UserProfile.objects.create(user=self.admin, role='administrator')
        
        # Vet User
        self.vet = User.objects.create_user(
            username='vet_filter', password='password123'
        )
        UserProfile.objects.create(user=self.vet, role='veterinarian')
        
        # Clean current logs
        ActivityLog.objects.all().delete()
        
        # Add mock logs
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        two_days_ago = now - datetime.timedelta(days=2)
        
        # Log 1: admin_filter create dashboard 2 days ago
        self.log1 = ActivityLog.objects.create(
            user=self.admin,
            user_role='administrator',
            action_type='create',
            module_accessed='dashboard',
            description='Test log 1',
            timestamp=two_days_ago
        )
        # Update timestamp manually because auto_now_add makes it read-only during save()
        ActivityLog.objects.filter(pk=self.log1.pk).update(timestamp=two_days_ago)
        
        # Log 2: vet_filter view animals yesterday
        self.log2 = ActivityLog.objects.create(
            user=self.vet,
            user_role='veterinarian',
            action_type='view',
            module_accessed='animals',
            description='Test log 2',
            timestamp=yesterday
        )
        ActivityLog.objects.filter(pk=self.log2.pk).update(timestamp=yesterday)
        
        # Log 3: admin_filter update devices today
        self.log3 = ActivityLog.objects.create(
            user=self.admin,
            user_role='administrator',
            action_type='update',
            module_accessed='devices',
            description='Test log 3',
            timestamp=now
        )
        ActivityLog.objects.filter(pk=self.log3.pk).update(timestamp=now)

        self.logs_url = reverse('logs:dashboard')
        self.client.login(username='admin_filter', password='password123')
        # Clear the login activity log generated by self.client.login() to avoid skewing test counts
        ActivityLog.objects.filter(action_type='login').delete()

    def test_search_by_username(self):
        """Test search query filters logs by username"""
        response = self.client.get(self.logs_url, {'search': 'vet_filter'})
        self.assertEqual(response.status_code, 200)
        logs = response.context['page_obj'].object_list
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].user, self.vet)

    def test_filter_by_role(self):
        """Test role dropdown filters logs"""
        response = self.client.get(self.logs_url, {'role': 'administrator'})
        self.assertEqual(response.status_code, 200)
        logs = response.context['page_obj'].object_list
        self.assertEqual(len(logs), 2)
        for log in logs:
            self.assertEqual(log.user_role, 'administrator')

    def test_filter_by_action_type(self):
        """Test action_type filter works"""
        response = self.client.get(self.logs_url, {'action_type': 'view'})
        self.assertEqual(response.status_code, 200)
        logs = response.context['page_obj'].object_list
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].action_type, 'view')

    def test_filter_by_module(self):
        """Test module filter works"""
        response = self.client.get(self.logs_url, {'module_accessed': 'devices'})
        self.assertEqual(response.status_code, 200)
        logs = response.context['page_obj'].object_list
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].module_accessed, 'devices')

    def test_filter_by_date_range(self):
        """Test date range filters work"""
        today_str = timezone.now().date().isoformat()
        yesterday_str = (timezone.now() - datetime.timedelta(days=1)).date().isoformat()
        two_days_ago_str = (timezone.now() - datetime.timedelta(days=2)).date().isoformat()
        
        # Test start_date only
        response = self.client.get(self.logs_url, {'start_date': today_str})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj'].object_list), 1)
        
        # Test end_date only
        response = self.client.get(self.logs_url, {'end_date': yesterday_str})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj'].object_list), 2)
        
        # Test range
        response = self.client.get(self.logs_url, {
            'start_date': two_days_ago_str,
            'end_date': yesterday_str
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj'].object_list), 2)
