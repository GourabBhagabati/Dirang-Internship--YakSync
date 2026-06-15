from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UserProfile
from io import BytesIO
from PIL import Image
import os

class ProfileEditViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='farm_operator',
            phone_number='1234567890'
        )
        self.edit_url = reverse('authentication:profile_edit')

    def test_profile_edit_view_requires_login(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_profile_edit_view_get_success(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/profile_edit.html')
        self.assertIn('user_form', response.context)
        self.assertIn('profile_form', response.context)

    def test_profile_edit_view_post_success(self):
        self.client.login(username='testuser', password='testpassword123')
        
        # Dynamically generate a valid PNG image in memory
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        test_image = SimpleUploadedFile(
            name='test_avatar.png',
            content=img_io.read(),
            content_type='image/png'
        )
        
        data = {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'email': 'updated@example.com',
            'phone_number': '9876543210',
            'profile_image': test_image
        }
        
        response = self.client.post(self.edit_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify database updates
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        
        self.assertEqual(self.user.first_name, 'UpdatedFirst')
        self.assertEqual(self.user.last_name, 'UpdatedLast')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.profile.phone_number, '9876543210')
        self.assertTrue(self.profile.profile_image.name.startswith('profiles/test_avatar'))
        
        # Clean up files created
        if self.profile.profile_image and os.path.exists(self.profile.profile_image.path):
            os.remove(self.profile.profile_image.path)

    def test_profile_edit_view_post_invalid_image_extension(self):
        self.client.login(username='testuser', password='testpassword123')
        
        # Generate valid image structure but name it with invalid extension (.pdf)
        img = Image.new('RGB', (100, 100), color='blue')
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        invalid_file = SimpleUploadedFile(
            name='test.pdf',
            content=img_io.read(),
            content_type='application/pdf'
        )
        
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone_number': '1234567890',
            'profile_image': invalid_file
        }
        
        response = self.client.post(self.edit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            'profile_form',
            'profile_image',
            'Unsupported file extension. Only JPG, JPEG, and PNG are allowed.'
        )

    def test_profile_edit_view_creates_profile_if_missing(self):
        # Delete profile to simulate a superuser or old account without a profile
        self.profile.delete()
        
        self.client.login(username='testuser', password='testpassword123')
        
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        
        # Verify that UserProfile was created automatically
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
