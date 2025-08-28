from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, organization

class UserAuthenticationTests(APITestCase):
    """
        Test suite for user registration, login, profile and logout functionalities
    """

    def setUp(self):
        self.register_url = reverse('user-registration')
        self.login_url = reverse('token-obtain-pair')
        self.profile_url = reverse('user-profile')
        self.logout_url = reverse('user-logout')

        self.user_data ={
            "email":"lainkali400@gmail.com",
            "name":"Alain",
            "password":"strongpassword@123",
            "role":"Recruiter",
            "organization_name":"Test Corp"
        }

    def test_user_registration_success(self):
        """
        Ensure a new user can be registered successfully.
        """
        response = self.client.post(self.register_url,self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(),1)
        self.assertEqual(organization.objects.count(),1)
        self.assertEqual(User.objects.get().email,self.user_data['email'])
        self.assertEqual(organization.objects.get().name,self.user_data['organization_name'])
    
    def test_user_login_and_get_profile(self):
        """
        Ensure a register user can log in and retrieve their profile.
        """
        self.client.post(self.register_url,self.user_data, format='json')
        
        login_data ={
            "email":self.user_data['email'],
            "password":self.user_data['password']
        }
        response = self.client.post(self.login_url,login_data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertIn('access',response.data)
        self.assertIn('refresh',response.data)

        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get(self.profile_url)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['email'],self.user_data['email'])
        self.assertEqual(profile_response.data['organization']['name'],self.user_data['organization_name'])
    
    def test_user_logout(self):
        """
        Ensure a logged-in user can successfully log out.
        """
        # Register and log in the user to get tokens
        self.client.post(self.register_url, self.user_data, format='json')
        login_response = self.client.post(self.login_url, {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }, format='json')
        
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']

        # Authenticate for the logout request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Send the logout request with the refresh token
        logout_response = self.client.post(self.logout_url, {"refresh": refresh_token}, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)
    
    def test_registration_with_existing_organization(self):
        """
        Ensure a new user can register with an existing organization.
        """
        # Create the first user and organization
        self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(organization.objects.count(), 1)

        # Create a second user with the same organization name
        second_user_data = {
            "email": "testuser2@example.com",
            "name": "Test User 2",
            "password": "strongpassword123",
            "role": "Evaluator",
            "organization_name": "Test Corp" # Same organization
        }
        response = self.client.post(self.register_url, second_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify no new organization was created
        self.assertEqual(organization.objects.count(), 1)
        self.assertEqual(User.objects.count(), 2)
    
    
