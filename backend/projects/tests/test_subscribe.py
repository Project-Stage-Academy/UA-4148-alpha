from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone

from projects.models import StartupProject as Project, Subscription
from profiles.models import StartupProfile, InvestorProfile
from users.models import UserRole

User = get_user_model()

class SubscriptionTests(APITestCase):
    def setUp(self):
        self.investor_role = UserRole.objects.create(role="investor")
        self.user_role = UserRole.objects.create(role="user")

        self.investor_user = User.objects.create_user(
            email="investor@example.com",
            password="testpass123",
            role=self.investor_role,
            username="investor"
        )
        self.non_investor_user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            role=self.user_role,
            username="user"
        )
        self.startup_user = User.objects.create_user(
            email="startup@example.com",
            password="testpass123",
            username="startup_user",
            role=self.user_role
        )

        self.startup_profile = StartupProfile.objects.create(user=self.startup_user)
        self.investor_profile = InvestorProfile.objects.create(user=self.investor_user)

        self.project = Project.objects.create(
            subject="Test Project",
            idea="Test idea",
            description="Test Desc",
            funding_goal=Decimal("1000.00"),
            startup=self.startup_profile,
        )

    def test_investor_can_subscribe(self):
        self.client.force_authenticate(user=self.investor_user)
        try:
            url = reverse('project-subscribe', args=[self.project.id])
        except Exception:
            url = f'/api/projects/{self.project.id}/subscribe/'
        data = {"share": "100.00", "project": self.project.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)
        sub = Subscription.objects.first()
        self.assertEqual(sub.investor, self.investor_profile)
        self.assertEqual(sub.project, self.project)
        self.assertEqual(sub.share, Decimal("100.00"))

    def test_non_investor_cannot_subscribe(self):
        self.client.force_authenticate(user=self.non_investor_user)
        try:
            url = reverse('project-subscribe', args=[self.project.id])
        except Exception:
            url = f'/api/projects/{self.project.id}/subscribe/'
        data = {"share": "100.00", "project": self.project.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_subscribe_to_fully_funded_project(self):
        Subscription.objects.create(
            project=self.project,
            investor=self.investor_profile,
            share=self.project.funding_goal,
            created_at=timezone.now()
        )
        self.client.force_authenticate(user=self.investor_user)
        try:
            url = reverse('project-subscribe', args=[self.project.id])
        except Exception:
            url = f'/api/projects/{self.project.id}/subscribe/'
        response = self.client.post(url, {"share": "10.00", "project": self.project.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data.get("non_field_errors") or response.data.get("error") or response.data
        self.assertIn("Funding goal already reached", str(errors))
