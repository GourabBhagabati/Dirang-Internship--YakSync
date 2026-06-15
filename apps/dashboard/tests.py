from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from apps.alerts.models import Alert

class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.dashboard_url = reverse('dashboard:index')

    def test_dashboard_requires_login(self):
        """Test that accessing the dashboard requires authentication"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    @patch('apps.dashboard.views.get_weather_data')
    def test_dashboard_with_weather_data(self, mock_get_weather):
        """Test dashboard rendering with successful weather data"""
        mock_get_weather.return_value = {
            'temperature': 18.5,
            'humidity': 75,
            'condition': 'Partly Cloudy',
            'wind_speed': 3.2,
            'last_updated': '2026-06-15 12:00',
            'source': 'WeatherAPI'
        }
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dirang')
        self.assertContains(response, '18.5°C')
        self.assertContains(response, '75%')
        self.assertContains(response, 'Partly Cloudy')
        self.assertContains(response, '3.2 m/s')
        self.assertContains(response, 'Obs: 2026-06-15 12:00')

    @patch('apps.dashboard.views.get_weather_data')
    def test_dashboard_weather_unavailable(self, mock_get_weather):
        """Test dashboard rendering with weather service failing (None)"""
        mock_get_weather.return_value = None
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Weather information currently unavailable')

    def test_dashboard_alert_contexts(self):
        """Test that alert counts and unread critical counts are correctly passed via context processors"""
        # Create a critical alert
        Alert.objects.create(
            title='Critical Temp Alert',
            alert_type='temperature',
            severity='critical',
            description='Critical high temperature detected',
            status='active'
        )
        
        # Create a warning alert
        Alert.objects.create(
            title='Warning Battery Alert',
            alert_type='low_battery',
            severity='warning',
            description='Battery low',
            status='active'
        )

        # Create a resolved alert (should not be in unread/active dropdown lists)
        Alert.objects.create(
            title='Resolved Alert',
            alert_type='movement',
            severity='critical',
            description='Animal moved normally',
            status='resolved'
        )

        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        
        # Check context variables from the context processor
        self.assertEqual(response.context['unread_critical_count'], 1)
        self.assertEqual(len(response.context['recent_active_alerts']), 2)
        
        # Verify navbar rendering of alerts and badges
        self.assertContains(response, 'Critical Temp Alert')
        self.assertContains(response, 'Warning Battery Alert')
        self.assertNotContains(response, 'Resolved Alert')
        self.assertContains(response, 'notification-badge')
