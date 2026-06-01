from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="validuser",
            email="valid@example.com",
            password="correct-password",
        )

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "validuser", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_login_rejects_wrong_username(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "missinguser", "password": "correct-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_login_accepts_exact_credentials(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "validuser", "password": "correct-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "validuser")

    def test_login_token_can_load_profile(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {"username": "validuser", "password": "correct-password"},
            format="json",
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )
        profile_response = self.client.get("/api/auth/profile/")

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data["username"], "validuser")

    def test_login_accepts_email_credentials(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "valid@example.com", "password": "correct-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "validuser")


class RegisterTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_returns_tokens_and_user(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "correct-password",
                "phone": "",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")
