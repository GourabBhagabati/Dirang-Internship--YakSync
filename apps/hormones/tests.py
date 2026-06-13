from datetime import datetime, timezone
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from apps.animals.models import Animal
from .models import HormoneRelease, HormoneReservoir
from .views import (
    HormoneReleaseCreateView,
    HormoneReleaseDetailView,
    HormoneReleaseListView,
    HormoneReservoirCreateView,
    HormoneReservoirDeleteView,
    HormoneReservoirDetailView,
    HormoneReservoirListView,
    HormoneReservoirUpdateView,
)


class HormoneModuleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='hormone_user',
            password='StrongPass123',
            first_name='Test',
            last_name='Veterinarian',
        )
        self.other_user = User.objects.create_user(
            username='other_user',
            password='StrongPass123',
        )
        self.animal = Animal.objects.create(
            animal_id='YAK-H01',
            name='Dolma',
            species='Yak',
            breed='Himalayan',
            age=4,
            gender='female',
            weight=Decimal('315.50'),
            health_status='healthy',
            reproductive_status='cycling',
            created_by=self.user,
        )
        self.other_animal = Animal.objects.create(
            animal_id='YAK-H02',
            name='Pema',
            species='Yak',
            breed='Himalayan',
            age=5,
            gender='female',
            weight=Decimal('330.00'),
            health_status='healthy',
            reproductive_status='pregnant',
            created_by=self.user,
        )
        self.reservoir = HormoneReservoir.objects.create(
            hormone_type='Progesterone',
            initial_quantity=Decimal('100.00'),
            current_quantity=Decimal('100.00'),
            unit='ml',
            low_threshold=Decimal('20.00'),
        )
        self.low_reservoir = HormoneReservoir.objects.create(
            hormone_type='Oxytocin',
            initial_quantity=Decimal('50.00'),
            current_quantity=Decimal('5.00'),
            unit='ml',
            low_threshold=Decimal('10.00'),
        )

    def login(self):
        self.client.login(username='hormone_user', password='StrongPass123')

    def create_release(
        self,
        animal=None,
        reservoir=None,
        quantity='5.00',
        performed_by=None,
        timestamp=None,
    ):
        release = HormoneRelease.objects.create(
            animal=animal or self.animal,
            reservoir=reservoir or self.reservoir,
            quantity=Decimal(quantity),
            performed_by=performed_by or self.user,
            notes='Routine release',
        )
        if timestamp:
            HormoneRelease.objects.filter(pk=release.pk).update(timestamp=timestamp)
            release.refresh_from_db()
        return release

    def test_hormone_urls_resolve(self):
        url_map = {
            'hormones:reservoir_list': HormoneReservoirListView,
            'hormones:reservoir_create': HormoneReservoirCreateView,
            'hormones:release_list': HormoneReleaseListView,
            'hormones:release_create': HormoneReleaseCreateView,
        }

        for url_name, view_class in url_map.items():
            self.assertEqual(resolve(reverse(url_name)).func.view_class, view_class)

        detail_url_map = {
            reverse('hormones:reservoir_detail', kwargs={'pk': self.reservoir.pk}): HormoneReservoirDetailView,
            reverse('hormones:reservoir_edit', kwargs={'pk': self.reservoir.pk}): HormoneReservoirUpdateView,
            reverse('hormones:reservoir_delete', kwargs={'pk': self.reservoir.pk}): HormoneReservoirDeleteView,
            reverse('hormones:release_detail', kwargs={'pk': self.create_release().pk}): HormoneReleaseDetailView,
        }
        for url, view_class in detail_url_map.items():
            self.assertEqual(resolve(url).func.view_class, view_class)

    def test_hormone_views_require_login(self):
        protected_urls = [
            reverse('hormones:reservoir_list'),
            reverse('hormones:reservoir_create'),
            reverse('hormones:reservoir_detail', kwargs={'pk': self.reservoir.pk}),
            reverse('hormones:release_list'),
            reverse('hormones:release_create'),
        ]

        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/auth/login/', response.url)

    def test_reservoir_crud_operations(self):
        self.login()

        create_response = self.client.post(reverse('hormones:reservoir_create'), {
            'hormone_type': 'Estradiol',
            'initial_quantity': '75.00',
            'current_quantity': '70.00',
            'unit': 'mg',
            'low_threshold': '15.00',
        })
        self.assertRedirects(create_response, reverse('hormones:reservoir_list'))
        reservoir = HormoneReservoir.objects.get(hormone_type='Estradiol')

        detail_response = self.client.get(reverse('hormones:reservoir_detail', kwargs={'pk': reservoir.pk}))
        self.assertTemplateUsed(detail_response, 'hormones/reservoir_detail.html')
        self.assertContains(detail_response, 'Estradiol')

        update_response = self.client.post(reverse('hormones:reservoir_edit', kwargs={'pk': reservoir.pk}), {
            'hormone_type': 'Estradiol',
            'initial_quantity': '75.00',
            'current_quantity': '60.00',
            'unit': 'mg',
            'low_threshold': '15.00',
        })
        self.assertRedirects(update_response, reverse('hormones:reservoir_detail', kwargs={'pk': reservoir.pk}))
        reservoir.refresh_from_db()
        self.assertEqual(reservoir.current_quantity, Decimal('60.00'))

        delete_response = self.client.post(reverse('hormones:reservoir_delete', kwargs={'pk': reservoir.pk}))
        self.assertRedirects(delete_response, reverse('hormones:reservoir_list'))
        self.assertFalse(HormoneReservoir.objects.filter(pk=reservoir.pk).exists())

    def test_reservoir_filters_and_pagination(self):
        self.login()
        for index in range(11):
            HormoneReservoir.objects.create(
                hormone_type=f'GnRH {index}',
                initial_quantity=Decimal('30.00'),
                current_quantity=Decimal('30.00'),
                unit='ml',
                low_threshold=Decimal('5.00'),
            )

        response = self.client.get(reverse('hormones:reservoir_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hormones/reservoir_list.html')
        self.assertEqual(len(response.context['reservoirs']), 10)
        self.assertTrue(response.context['is_paginated'])

        search_response = self.client.get(reverse('hormones:reservoir_list'), {'search': 'Progesterone'})
        self.assertContains(search_response, 'Progesterone')
        self.assertNotContains(search_response, 'Oxytocin')

        low_response = self.client.get(reverse('hormones:reservoir_list'), {'low_stock': 'on'})
        self.assertContains(low_response, 'Oxytocin')
        self.assertNotContains(low_response, 'Progesterone')

    def test_release_create_reduces_inventory(self):
        self.login()

        response = self.client.post(reverse('hormones:release_create'), {
            'animal': str(self.animal.pk),
            'reservoir': str(self.reservoir.pk),
            'quantity': '25.00',
            'notes': 'Scheduled reproductive protocol',
        })

        release = HormoneRelease.objects.get(quantity=Decimal('25.00'))
        self.assertRedirects(response, reverse('hormones:release_detail', kwargs={'pk': release.pk}))
        self.reservoir.refresh_from_db()
        self.assertEqual(self.reservoir.current_quantity, Decimal('75.00'))
        self.assertEqual(release.performed_by, self.user)
        self.assertEqual(release.notes, 'Scheduled reproductive protocol')

    def test_release_prevents_negative_inventory(self):
        self.login()

        response = self.client.post(reverse('hormones:release_create'), {
            'animal': str(self.animal.pk),
            'reservoir': str(self.low_reservoir.pk),
            'quantity': '10.00',
            'notes': 'Too much',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hormones/release_form.html')
        self.assertContains(response, 'Release quantity exceeds available reservoir quantity')
        self.assertFalse(HormoneRelease.objects.filter(notes='Too much').exists())
        self.low_reservoir.refresh_from_db()
        self.assertEqual(self.low_reservoir.current_quantity, Decimal('5.00'))

    def test_release_filters_and_pagination(self):
        self.login()
        target_release = self.create_release(
            animal=self.animal,
            reservoir=self.reservoir,
            quantity='4.00',
            performed_by=self.user,
            timestamp=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        )
        self.create_release(
            animal=self.other_animal,
            reservoir=self.low_reservoir,
            quantity='2.00',
            performed_by=self.other_user,
            timestamp=datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc),
        )
        for index in range(11):
            self.create_release(quantity=str(index + 1))

        response = self.client.get(reverse('hormones:release_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hormones/release_list.html')
        self.assertEqual(len(response.context['releases']), 10)
        self.assertTrue(response.context['is_paginated'])

        filtered_response = self.client.get(reverse('hormones:release_list'), {
            'animal': str(self.animal.pk),
            'hormone_type': 'Progesterone',
            'user': str(self.user.pk),
            'start_date': '2026-03-01',
            'end_date': '2026-03-01',
        })
        self.assertContains(filtered_response, '4.00')
        self.assertNotContains(filtered_response, 'Oxytocin')
        self.assertIn(target_release, filtered_response.context['releases'])

    def test_release_detail_template_renders(self):
        self.login()
        release = self.create_release(quantity='6.00')

        response = self.client.get(reverse('hormones:release_detail', kwargs={'pk': release.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hormones/release_detail.html')
        self.assertContains(response, 'Release Information')
        self.assertContains(response, 'Progesterone')
