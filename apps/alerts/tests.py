from datetime import datetime, timezone
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from apps.animals.models import Animal
from apps.devices.models import Device
from apps.monitoring.models import SensorReading
from apps.alerts.models import Alert


class AlertSystemTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='vet_operator',
            password='Password123'
        )
        
        # Create animal
        self.animal = Animal.objects.create(
            animal_id='YAK-010',
            name='Norbu',
            species='Yak',
            breed='Himalayan',
            age=3,
            gender='female',
            weight=Decimal('280.00'),
            health_status='healthy',
            reproductive_status='not_cycling',
            created_by=self.user
        )
        
        # Create device
        self.device = Device.objects.create(
            device_id='DEV-100',
            name='Collar GPS',
            device_type='sensor',
            installation_location='North Pasture',
            status='active',
            battery_level=90,
            assigned_animal=self.animal
        )

    def test_normal_reading_does_not_trigger_alert(self):
        """Verify normal readings do not flag abnormal or create alerts"""
        reading = SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='temperature',
            value=Decimal('38.50'),
            unit='celsius'
        )
        
        self.assertFalse(reading.is_abnormal)
        self.assertEqual(Alert.objects.count(), 0)

    def test_high_temperature_triggers_critical_alert(self):
        """Verify body temp > 39.5 triggers critical alert"""
        reading = SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='temperature',
            value=Decimal('39.85'),
            unit='celsius'
        )
        
        self.assertTrue(reading.is_abnormal)
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.first()
        self.assertEqual(alert.severity, 'critical')
        self.assertEqual(alert.alert_type, 'temperature')
        self.assertEqual(alert.animal, self.animal)
        self.assertEqual(alert.device, self.device)
        self.assertEqual(alert.sensor_reading, reading)
        self.assertIn("high body temperature", alert.description)

    def test_low_temperature_triggers_warning_alert(self):
        """Verify body temp < 37.5 triggers warning alert"""
        reading = SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='temperature',
            value=Decimal('37.10'),
            unit='celsius'
        )
        
        self.assertTrue(reading.is_abnormal)
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.first()
        self.assertEqual(alert.severity, 'warning')
        self.assertEqual(alert.alert_type, 'temperature')
        self.assertIn("low body temperature", alert.description)

    def test_no_movement_triggers_critical_alert(self):
        """Verify movement == 0 triggers critical alert"""
        reading = SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='movement',
            value=Decimal('0.00'),
            unit='steps'
        )
        
        self.assertTrue(reading.is_abnormal)
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.first()
        self.assertEqual(alert.severity, 'critical')
        self.assertEqual(alert.alert_type, 'movement')
        self.assertIn("no movement", alert.description)

    def test_low_movement_triggers_warning_alert(self):
        """Verify movement < 100 triggers warning alert"""
        reading = SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='movement',
            value=Decimal('45.00'),
            unit='steps'
        )
        
        self.assertTrue(reading.is_abnormal)
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.first()
        self.assertEqual(alert.severity, 'warning')
        self.assertEqual(alert.alert_type, 'movement')
        self.assertIn("low movement", alert.description)

    def test_excessive_movement_triggers_warning_alert(self):
        """Verify movement > 10000 triggers warning alert"""
        reading = SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='movement',
            value=Decimal('10500.00'),
            unit='steps'
        )
        
        self.assertTrue(reading.is_abnormal)
        self.assertEqual(Alert.objects.count(), 1)
        alert = Alert.objects.first()
        self.assertEqual(alert.severity, 'warning')
        self.assertEqual(alert.alert_type, 'movement')
        self.assertIn("excessive movement", alert.description)

    def test_acknowledge_alert_view(self):
        """Verify that posting to acknowledge view updates status, user, and timestamp"""
        reading = SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='temperature',
            value=Decimal('40.00'),
            unit='celsius'
        )
        alert = Alert.objects.first()
        self.assertEqual(alert.status, 'active')
        
        self.client.login(username='vet_operator', password='Password123')
        response = self.client.post(reverse('alerts:acknowledge', kwargs={'pk': alert.pk}))
        
        self.assertEqual(response.status_code, 302)
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'acknowledged')
        self.assertEqual(alert.acknowledged_by, self.user)
        self.assertIsNotNone(alert.acknowledged_at)

    def test_resolve_alert_view(self):
        """Verify that posting to resolve view updates status, user, and timestamp"""
        reading = SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='movement',
            value=Decimal('0.00'),
            unit='steps'
        )
        alert = Alert.objects.first()
        self.assertEqual(alert.status, 'active')
        
        self.client.login(username='vet_operator', password='Password123')
        response = self.client.post(reverse('alerts:resolve', kwargs={'pk': alert.pk}))
        
        self.assertEqual(response.status_code, 302)
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'resolved')
        self.assertEqual(alert.resolved_by, self.user)
        self.assertIsNotNone(alert.resolved_at)

    def test_alert_list_view_filters(self):
        """Verify that alert dashboard renders correctly and handles filters"""
        # Create critical alert
        SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='temperature',
            value=Decimal('40.00'),
            unit='celsius'
        )
        # Create warning alert
        SensorReading.objects.create(
            animal=self.animal,
            device=self.device,
            sensor_type='movement',
            value=Decimal('50.00'),
            unit='steps'
        )
        
        self.client.login(username='vet_operator', password='Password123')
        response = self.client.get(reverse('alerts:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['alerts']), 2)
        
        # Filter by severity = critical
        response_critical = self.client.get(reverse('alerts:dashboard'), {'severity': 'critical'})
        self.assertEqual(len(response_critical.context['alerts']), 1)
        self.assertEqual(response_critical.context['alerts'][0].severity, 'critical')
        
        # Filter by alert_type = movement
        response_movement = self.client.get(reverse('alerts:dashboard'), {'alert_type': 'movement'})
        self.assertEqual(len(response_movement.context['alerts']), 1)
        self.assertEqual(response_movement.context['alerts'][0].alert_type, 'movement')
