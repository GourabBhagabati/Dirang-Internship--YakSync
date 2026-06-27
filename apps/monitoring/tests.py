from datetime import datetime, timezone
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from apps.animals.models import Animal
from apps.devices.models import Device
from .models import SensorReading
from .views import SensorReadingDetailView, SensorReadingListView


class MonitoringViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='monitor_user',
            password='StrongPass123',
        )
        self.animal = Animal.objects.create(
            animal_id='YAK-001',
            name='Dawa',
            species='Yak',
            breed='Himalayan',
            age=4,
            gender='female',
            weight=Decimal('310.50'),
            health_status='healthy',
            reproductive_status='cycling',
            created_by=self.user,
        )
        self.other_animal = Animal.objects.create(
            animal_id='YAK-002',
            name='Lhamo',
            species='Yak',
            breed='Himalayan',
            age=5,
            gender='female',
            weight=Decimal('328.75'),
            health_status='healthy',
            reproductive_status='pregnant',
            created_by=self.user,
        )
        self.device = Device.objects.create(
            device_id='DEV-001',
            name='Collar Sensor',
            device_type='sensor',
            installation_location='North Pen',
            status='active',
            battery_level=87,
            assigned_animal=self.animal,
        )
        self.other_device = Device.objects.create(
            device_id='DEV-002',
            name='Barn Sensor',
            device_type='sensor',
            installation_location='South Pen',
            status='active',
            battery_level=74,
            assigned_animal=self.other_animal,
        )
        self.normal_reading = self.create_reading(
            animal=self.animal,
            device=self.device,
            sensor_type='temperature',
            value='38.4000',
            unit='celsius',
            timestamp=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
        )
        self.abnormal_reading = self.create_reading(
            animal=self.other_animal,
            device=self.other_device,
            sensor_type='movement',
            value='9500.0000',
            unit='steps',
            is_abnormal=True,
            timestamp=datetime(2026, 2, 2, 11, 0, tzinfo=timezone.utc),
        )

    def create_reading(
        self,
        animal,
        device,
        sensor_type='temperature',
        value='37.5000',
        unit='celsius',
        is_abnormal=False,
        timestamp=None,
    ):
        reading = SensorReading.objects.create(
            animal=animal,
            device=device,
            sensor_type=sensor_type,
            value=Decimal(value),
            unit=unit,
            is_abnormal=is_abnormal,
        )
        if timestamp:
            SensorReading.objects.filter(pk=reading.pk).update(timestamp=timestamp)
            reading.refresh_from_db()
        return reading

    def test_monitoring_urls_resolve(self):
        list_match = resolve(reverse('monitoring:list'))
        detail_match = resolve(reverse('monitoring:detail', kwargs={'pk': self.normal_reading.pk}))

        self.assertEqual(list_match.func.view_class, SensorReadingListView)
        self.assertEqual(detail_match.func.view_class, SensorReadingDetailView)

    def test_monitoring_views_require_login(self):
        list_response = self.client.get(reverse('monitoring:list'))
        detail_response = self.client.get(reverse('monitoring:detail', kwargs={'pk': self.normal_reading.pk}))

        self.assertRedirects(
            list_response,
            f"/auth/login/?next={reverse('monitoring:list')}",
        )
        self.assertRedirects(
            detail_response,
            f"/auth/login/?next={reverse('monitoring:detail', kwargs={'pk': self.normal_reading.pk})}",
        )

    def test_list_renders_with_pagination(self):
        self.client.login(username='monitor_user', password='StrongPass123')
        for index in range(11):
            self.create_reading(
                animal=self.animal,
                device=self.device,
                value=str(37 + index),
                timestamp=datetime(2026, 2, 3, index, 0, tzinfo=timezone.utc),
            )

        response = self.client.get(reverse('monitoring:list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'monitoring/sensor_reading_list.html')
        self.assertEqual(len(response.context['readings']), 10)
        self.assertTrue(response.context['is_paginated'])
        self.assertContains(response, 'Sensor Monitoring')

    def test_list_filters_readings(self):
        self.client.login(username='monitor_user', password='StrongPass123')

        abnormal_response = self.client.get(
            reverse('monitoring:list'),
            {'abnormal_only': 'on'},
        )
        self.assertContains(abnormal_response, '9500.0000')
        self.assertNotContains(abnormal_response, '38.4000')

        filtered_response = self.client.get(
            reverse('monitoring:list'),
            {
                'animal': str(self.animal.pk),
                'device': str(self.device.pk),
                'sensor_type': 'temperature',
                'start_date': '2026-02-01',
                'end_date': '2026-02-01',
                'search': 'Collar',
            },
        )
        self.assertContains(filtered_response, '38.4000')
        self.assertNotContains(filtered_response, '9500.0000')

        invalid_response = self.client.get(
            reverse('monitoring:list'),
            {'animal': 'invalid'},
        )
        self.assertEqual(invalid_response.status_code, 200)
        self.assertEqual(len(invalid_response.context['readings']), 0)

    def test_detail_renders_related_history(self):
        self.client.login(username='monitor_user', password='StrongPass123')
        history_reading = self.create_reading(
            animal=self.animal,
            device=self.device,
            sensor_type='temperature',
            value='38.1000',
            unit='celsius',
            timestamp=datetime(2026, 2, 1, 9, 0, tzinfo=timezone.utc),
        )

        response = self.client.get(reverse('monitoring:detail', kwargs={'pk': self.normal_reading.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'monitoring/sensor_reading_detail.html')
        self.assertContains(response, 'Reading Information')
        self.assertIn(history_reading, response.context['related_history'])


class TelemetryAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='api_user', password='StrongPass123')
        self.animal = Animal.objects.create(
            animal_id='YAK-777',
            name='Gyamu',
            species='Yak',
            breed='Himalayan',
            age=3,
            gender='female',
            weight=Decimal('280.00'),
            health_status='healthy',
            reproductive_status='cycling',
            created_by=self.user
        )
        self.device = Device.objects.create(
            device_id='DEV-777',
            name='Collar 777',
            device_type='sensor',
            installation_location='North Pen',
            status='active',
            battery_level=90,
            assigned_animal=self.animal
        )
        # Create readings
        SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='temperature',
            value=Decimal('38.2000'),
            unit='celsius'
        )
        SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='movement',
            value=Decimal('450.0000'),
            unit='steps'
        )

    def test_unauthenticated_api_redirect(self):
        herd_url = reverse('monitoring:api_herd_telemetry')
        animal_url = reverse('monitoring:api_animal_telemetry', kwargs={'animal_id': self.animal.pk})
        
        response_herd = self.client.get(herd_url)
        self.assertEqual(response_herd.status_code, 302)
        
        response_animal = self.client.get(animal_url)
        self.assertEqual(response_animal.status_code, 302)

    def test_herd_telemetry_api(self):
        self.client.login(username='api_user', password='StrongPass123')
        url = reverse('monitoring:api_herd_telemetry')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = response.json()
        
        self.assertIn('temp_data', data)
        self.assertIn('move_data', data)
        self.assertEqual(len(data['temp_data']), 1)
        self.assertEqual(len(data['move_data']), 1)
        self.assertEqual(data['temp_data'][0]['value'], 38.2)
        self.assertEqual(data['move_data'][0]['value'], 450.0)

    def test_animal_telemetry_api(self):
        self.client.login(username='api_user', password='StrongPass123')
        url = reverse('monitoring:api_animal_telemetry', kwargs={'animal_id': self.animal.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = response.json()
        
        self.assertEqual(data['animal_id'], 'YAK-777')
        self.assertIn('temp_data', data)
        self.assertIn('move_data', data)
        self.assertEqual(len(data['temp_data']), 1)
        self.assertEqual(data['move_data'][0]['value'], 450.0)

    def test_animal_telemetry_api_404(self):
        self.client.login(username='api_user', password='StrongPass123')
        url = reverse('monitoring:api_animal_telemetry', kwargs={'animal_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

