from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

class CreateUserSerializerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/v1/auth/users/'

    def test_user_creation_successful(self):
        data = {
            'email': 'testuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'Password123!',
            're_password': 'Password123!',
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=data['email'])
        self.assertNotEqual(user.password, data['password'])
        self.assertTrue(user.check_password(data['password']))

    def test_user_creation_password_too_short(self):
        data = {
            'email': 'testuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'short',
            're_password': 'short',
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data) 

    def test_user_creation_missing_special_characters(self):
        data = {
            'email': 'testuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'Password123',
            're_password': 'Password123',
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_creation_passwords_do_not_match(self):
        data = {
            'email': 'testuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'Password123!',
            're_password': 'DifferentPassword123!',
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_creation_successful_with_special_characters_in_password(self):
        data = {
            'email': 'testuser@example.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'password': 'Valid123@',
            're_password': 'Valid123@',
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=data['email'])
        self.assertTrue(user.check_password(data['password']))
