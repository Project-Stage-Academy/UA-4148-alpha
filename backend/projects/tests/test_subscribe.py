from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from projects.models import Project, Subscription, Investor
from django.contrib.auth import get_user_model
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

        self.project = Project.objects.create(
            name="Test Project",
            description="Test Desc",
            budget=Decimal("1000.00")
        )

        self.investor = Investor.objects.create(
            name=self.investor_user.username,
            email=self.investor_user.email
        )

    def test_investor_can_subscribe(self):
        self.client.force_authenticate(user=self.investor_user)
        url = reverse('project-subscribe', args=[self.project.id])
        response = self.client.post(url, {
            "investor": self.investor.id,
            "share": "10",
            "investment_amount": "100.00"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscription.objects.count(), 1)

    def test_non_investor_cannot_subscribe(self):
        self.client.force_authenticate(user=self.non_investor_user)
        url = reverse('project-subscribe', args=[self.project.id])
        response = self.client.post(url, {
            "investor": self.investor.id,
            "share": "10",
            "investment_amount": "100.00"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_subscribe_to_fully_funded_project(self):
        Subscription.objects.create(
            investor=self.investor,
            project=self.project,
            share=100,
            investment_amount=self.project.budget
        )

        self.client.force_authenticate(user=self.investor_user)
        url = reverse('project-subscribe', args=[self.project.id])
        response = self.client.post(url, {
            "investor": self.investor.id,
            "share": "10",
            "investment_amount": "50.00"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("fully funded", response.data["error"])
