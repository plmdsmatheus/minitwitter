from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('user-register')
        self.login_url    = reverse('token-obtain-pair')
        self.refresh_url  = reverse('token-refresh')
        self.user_data    = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'strongpass123'
        }

    def test_register_user_success(self):
        """Registro com dados válidos deve retornar 201 e criar usuário."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify that the user was created
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        # Verify that the password is not returned in the response
        self.assertNotIn('password', response.data)

    def test_register_missing_fields(self):
        """ Missing email or password should return 400. """
        bad_data = {'username': 'x'}
        response = self.client.post(self.register_url, bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)

    def test_login_success(self):
        """Login with valid credentials should return 200 and tokens."""
        # First create the user
        User.objects.create_user(**self.user_data)
        resp = self.client.post(self.login_url, {
            'email':    self.user_data['email'],
            'password': self.user_data['password']
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

    def test_login_wrong_password(self):
        """Login with wrong password should return 401."""
        # First create the user
        User.objects.create_user(**self.user_data)
        resp = self.client.post(self.login_url, {
            'email':    self.user_data['email'],
            'password': 'wrongpass'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', resp.data)

    def test_refresh_token(self):
        """Refresh token should return new access token."""
        User.objects.create_user(**self.user_data)
        login_resp = self.client.post(self.login_url, {
            'email':    self.user_data['email'],
            'password': self.user_data['password']
        }, format='json')
        refresh_token = login_resp.data['refresh']
        refresh_resp = self.client.post(self.refresh_url, {
            'refresh': refresh_token
        }, format='json')
        self.assertEqual(refresh_resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_resp.data)
