from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.animals.models import Animal
from apps.devices.models import Device
from apps.alerts.models import Alert
from apps.protocols.models import TreatmentProtocol, TreatmentAssignment

class ReportsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='reportuser',
            password='testpassword123',
            email='report@example.com'
        )
        
        # Create mock data
        self.animal = Animal.objects.create(
            animal_id='YAK-001',
            name='Test Yak',
            species='Yak',
            breed='Tibetan',
            age=5,
            gender='female',
            weight=350.00,
            health_status='healthy',
            reproductive_status='cycling'
        )
        self.device = Device.objects.create(
            device_id='DEV-001',
            name='Test Collar',
            device_type='sensor',
            installation_location='Neck',
            status='active',
            battery_level=90
        )
        self.protocol = TreatmentProtocol.objects.create(
            name='Ovsynch Protocol',
            description='Standard synchronization protocol',
            duration_days=10
        )
        self.assignment = TreatmentAssignment.objects.create(
            protocol=self.protocol,
            animal=self.animal,
            start_date='2026-06-15',
            end_date='2026-06-25',
            status='in_progress',
            progress=50
        )
        
        self.dashboard_url = reverse('reports:dashboard')
        self.pdf_url = reverse('reports:pdf_export')

    def test_reports_dashboard_requires_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_reports_dashboard_get_success(self):
        self.client.login(username='reportuser', password='testpassword123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/report_dashboard.html')
        self.assertEqual(response.context['total_animals'], 1)
        self.assertEqual(response.context['active_devices'], 1)
        self.assertEqual(response.context['total_protocols'], 1)

    def test_reports_dashboard_animal_health_preview(self):
        self.client.login(username='reportuser', password='testpassword123')
        response = self.client.get(self.dashboard_url, {'report_type': 'animal_health'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('report_data', response.context)
        self.assertEqual(response.context['report_data']['report_type'], 'animal_health')
        self.assertEqual(len(response.context['report_data']['rows']), 1)

    def test_pdf_export_requires_login(self):
        response = self.client.get(self.pdf_url, {'report_type': 'animal_health'})
        self.assertEqual(response.status_code, 302)

    def test_pdf_export_animal_health_success(self):
        self.client.login(username='reportuser', password='testpassword123')
        response = self.client.get(self.pdf_url, {'report_type': 'animal_health'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="YakSync_Animal_Health_Report_', response['Content-Disposition'])

    def test_pdf_export_iot_monitoring_success(self):
        self.client.login(username='reportuser', password='testpassword123')
        response = self.client.get(self.pdf_url, {'report_type': 'iot_monitoring'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="YakSync_Iot_Monitoring_Report_', response['Content-Disposition'])

    def test_pdf_export_alert_history_success(self):
        self.client.login(username='reportuser', password='testpassword123')
        response = self.client.get(self.pdf_url, {'report_type': 'alert_history'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="YakSync_Alert_History_Report_', response['Content-Disposition'])

    def test_pdf_export_treatment_hormone_success(self):
        self.client.login(username='reportuser', password='testpassword123')
        response = self.client.get(self.pdf_url, {'report_type': 'treatment_hormone'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="YakSync_Treatment_Hormone_Report_', response['Content-Disposition'])

    def test_csv_export_requires_login(self):
        csv_url = reverse('reports:csv_export')
        response = self.client.get(csv_url, {'report_type': 'animal_health'})
        self.assertEqual(response.status_code, 302)

    def test_csv_export_animal_health_success(self):
        self.client.login(username='reportuser', password='testpassword123')
        csv_url = reverse('reports:csv_export')
        response = self.client.get(csv_url, {'report_type': 'animal_health'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="YakSync_Animal_Health_Report_', response['Content-Disposition'])
        
        # Verify CSV content
        content = response.content.decode('utf-8')
        lines = content.strip().split('\r\n')
        self.assertTrue(len(lines) > 1)
        self.assertIn('Animal ID', lines[0])
        self.assertIn('YAK-001', lines[1])
