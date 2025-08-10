from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword123', name='Test User')
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.refresh_url = reverse('token_refresh')
        self.logout_url = reverse('logout')

    def test_register_user(self):
        """
        Ensure we can create a new user account.
        """
        data = {'name': 'New User', 'email': 'new@example.com', 'password': 'newpassword123'}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(email='new@example.com').name, 'New User')

    def test_login_user(self):
        """
        Ensure we can log in a user and get tokens.
        """
        data = {'email': 'test@example.com', 'password': 'testpassword123'}
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('accessToken' in response.data['data'])
        self.assertTrue('refreshToken' in response.data['data'])

    def test_login_user_invalid_credentials(self):
        """
        Ensure login fails with invalid credentials.
        """
        data = {'email': 'test@example.com', 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_refresh_token(self):
        """
        Ensure we can refresh an access token.
        """
        login_data = {'email': 'test@example.com', 'password': 'testpassword123'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['data']['refreshToken']

        refresh_data = {'refresh': refresh_token}
        response = self.client.post(self.refresh_url, refresh_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_logout_user(self):
        """
        Ensure we can log out a user by blacklisting the refresh token.
        """
        login_data = {'email': 'test@example.com', 'password': 'testpassword123'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['data']['refreshToken']
        access_token = login_response.data['data']['accessToken']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        logout_data = {'refresh': refresh_token}
        response = self.client.post(self.logout_url, logout_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

        # Verify the token is blacklisted
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_requires_authentication(self):
        """
        Ensure logout fails if the user is not authenticated.
        """
        login_data = {'email': 'test@example.com', 'password': 'testpassword123'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['data']['refreshToken']

        logout_data = {'refresh': refresh_token}
        response = self.client.post(self.logout_url, logout_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
