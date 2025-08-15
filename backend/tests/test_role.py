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
        self.user = UserProfile.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="TestPass123!",
            role=self.role,
            first_name="Test",
            last_name="User"
        )
        self.url = reverse('user')  

    def test_create(self):
       pass

    def test_switch(self):
        pass

    def test_create_not_allowed_roles(self):
        pass
