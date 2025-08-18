import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from users.models import UserProfile, UserRole

@pytest.mark.django_db
class TestUserRole:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.role = UserRole.objects.create(role="tester")
        self.url = reverse('user-create-role')

    def test_create(self):
        data = {"role": "investor"}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 201
        assert UserRole.objects.filter(role="investor").exists()

    def test_duplicate(self):
        data = {"role": "investor"}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 201

        response_duplicate = self.client.post(self.url, data, format='json')
        assert response_duplicate.status_code == 400

    def test_switch(self):
        investorRole = UserRole.objects.create(role="investor")
        startupRole = UserRole.objects.create(role="startup")
        userData = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPassw0rd!",
            "first_name": "John",
            "last_name": "Doe",
            "role": investorRole
        }
        user = UserProfile.objects.create_user(**userData)
        self.client.force_authenticate(user=user)

        url = reverse('user-switch-role')
        response = self.client.post(url, {"role_id": startupRole.id}, format='json')

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.role == startupRole

    def test_switch_to_role_not_exist(self):
        userData = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPassw0rd!",
            "first_name": "John",
            "last_name": "Doe",
            "role": None
        }
        user = UserProfile.objects.create_user(**userData)
        self.client.force_authenticate(user=user)
    
        url = reverse('user-switch-role')
        response = self.client.post(url, {"role_id": 2}, format='json')
        assert response.status_code == 404

    def test_create_not_allowed_roles(self):
        data = {"role": "not_allowed_role_to_create"}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 400
        assert True
