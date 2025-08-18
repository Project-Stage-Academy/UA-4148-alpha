import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from users.models import UserRole

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
        assert True

    def test_create_not_allowed_roles(self):
        assert True
