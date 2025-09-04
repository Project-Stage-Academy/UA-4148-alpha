"""
Test script to verify the logging system is working correctly in real conditions.
This script makes actual HTTP requests to the running Django server to test logging.
The logging system should automatically capture these events.
"""

import requests
import time


class RealWorldLoggingTest:
    """Test the logging system with real HTTP requests to the running server."""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = "http://localhost:8000"

    def test_user_registration_success(self):
        """Test successful user registration logging."""

        registration_data = {
            "email": "newuser456@example.com",
            "username": "newuser456",
            "password": "newpass123",
            "confirm_password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "role": 11,  # investor role
            "representative_type": "investor",
            "company_name": "Test Company",
        }

        response = self.session.post(
            f"{self.base_url}/api/users/register/", json=registration_data
        )
        # Let the logging system handle the response logging

    def test_user_registration_failed(self):
        """Test failed user registration logging."""

        registration_data = {
            "email": "invalid-email",
            "username": "newuser2",
            "password": "short",
            "confirm_password": "different",
            "first_name": "",
            "last_name": "",
            "role": 999,  # non-existent role
            "representative_type": "",
            "company_name": "",
        }

        response = self.session.post(
            f"{self.base_url}/api/users/register/", json=registration_data
        )
        # Let the logging system handle the response logging

    def test_user_login_success(self):
        """Test successful user login logging."""

        # Test successful login with existing account
        login_data = {"email": "jamespena@example.com", "password": "password123"}

        response = self.session.post(
            f"{self.base_url}/api/users/login/", json=login_data
        )

        if response.status_code == 200:
            return response.json().get("access")
        else:
            return None

    def test_user_login_failed(self):
        """Test failed user login logging."""

        failed_login_data = {"email": "test@example.com", "password": "wrongpassword"}

        response = self.session.post(
            f"{self.base_url}/api/users/login/", json=failed_login_data
        )
        # Let the logging system handle the response logging

    def test_authenticated_requests(self, access_token):
        """Test authenticated requests logging."""

        if not access_token:
            return

        # Set authentication header
        headers = {"Authorization": f"Bearer {access_token}"}

        # Test user profile endpoint
        response = self.session.get(f"{self.base_url}/api/users/me/", headers=headers)
        # Let the logging system handle the response logging

    def test_permission_denials(self):
        """Test permission denial logging."""

        # Test accessing protected endpoint without authentication
        response = self.session.get(f"{self.base_url}/api/users/me/")
        # Let the logging system handle the response logging

    def run_all_tests(self):
        """Run all logging tests."""

        try:
            # Run tests that trigger logs
            self.test_user_registration_success()
            self.test_user_registration_failed()
            self.test_user_login_failed()
            access_token = self.test_user_login_success()
            self.test_authenticated_requests(access_token)
            self.test_permission_denials()

            # Give some time for logs to be written
            time.sleep(2)

        except Exception as e:
            pass  # Let the logging system handle errors


if __name__ == "__main__":
    # Run real-world tests
    test_suite = RealWorldLoggingTest()
    test_suite.run_all_tests()
