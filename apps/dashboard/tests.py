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


class WeatherCacheTests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    @patch('apps.dashboard.weather._fetch_weather_data')
    def test_weather_data_caching(self, mock_fetch):
        """Test that get_weather_data caches results and avoids calling fetch again"""
        mock_data = {
            'temperature': 20.0,
            'humidity': 60,
            'condition': 'Sunny',
            'wind_speed': 2.5,
            'last_updated': '2026-06-19 12:00',
            'source': 'Open-Meteo'
        }
        mock_fetch.return_value = mock_data

        from apps.dashboard.weather import get_weather_data
        
        # First call (cache miss)
        first_call = get_weather_data()
        self.assertEqual(first_call, mock_data)
        self.assertEqual(mock_fetch.call_count, 1)

        # Second call (cache hit)
        second_call = get_weather_data()
        self.assertEqual(second_call, mock_data)
        self.assertEqual(mock_fetch.call_count, 1)  # Should read from cache, not fetch again


class DashboardUpdatesAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='apiuser', password='apipassword123')
        self.updates_url = reverse('dashboard:updates_api')

    def test_unauthenticated_api_request_redirects(self):
        """Test that unauthenticated requests to the updates API are redirected to login"""
        response = self.client.get(self.updates_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_authenticated_api_request(self):
        """Test that authenticated requests return valid dynamic updates payload"""
        self.client.login(username='apiuser', password='apipassword123')
        response = self.client.get(self.updates_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        
        data = response.json()
        self.assertIn('unread_critical_count', data)
        self.assertIn('stats', data)
        self.assertIn('html', data)
        
        # Verify stats keys
        stats = data['stats']
        self.assertEqual(stats['total_animals'], 0)
        self.assertEqual(stats['total_devices'], 0)
        
        # Verify HTML fragments keys
        html = data['html']
        self.assertIn('navbar_alerts', html)
        self.assertIn('dashboard_alerts', html)
        self.assertIn('dashboard_activities', html)
        self.assertIn('dashboard_hormones', html)


