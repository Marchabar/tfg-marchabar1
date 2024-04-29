from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import JsonResponse
from django.test import Client, TestCase
from django.urls import reverse

from apps.users.models import CustomUser


class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse(
            "login"
        )  # Replace 'login' with the actual URL name of your login page
        self.dashboard_url = "/"
        self.username = "testuser"
        self.password = "testpassword"
        self.user = CustomUser.objects.create_user(
            username=self.username, password=self.password
        )

    def test_valid_login(self):
        response = self.client.post(
            self.login_url, {"username": self.username, "password": self.password}
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

    def test_invalid_login(self):
        response = self.client.post(
            self.login_url, {"username": "invaliduser", "password": "invalidpassword"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "success": False,
                "message": "Nombre de usuario o contraseña son inválidos.",
            },
        )


class LogoutViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")
        self.username = "testuser"
        self.password = "testpassword"
        self.user = CustomUser.objects.create_user(
            username=self.username, password=self.password
        )

    def test_logout(self):
        self.client.login(username="testuser", password="testpassword")

        response = self.client.post(reverse("logout"))

        self.assertEqual(response.status_code, 302)
        self.assertFalse("_auth_user_id" in self.client.session)


class SignUpViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("signup")
        self.username = "testuser"
        self.password = "Testpassword2024"

    def test_valid_signup(self):
        # Create a sample image file for avatar
        avatar_content = b"dummy_avatar_content"
        avatar = SimpleUploadedFile(
            "avatar.jpg", avatar_content, content_type="image/jpeg"
        )

        response = self.client.post(
            self.signup_url,
            {
                "username": self.username,
                "password": self.password,
                "avatar": avatar,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

    def test_duplicate_username_signup(self):
        # Create a user with the same username
        CustomUser.objects.create_user(username=self.username, password=self.password)

        # Create a sample image file for avatar
        avatar_content = b"dummy_avatar_content"
        avatar = SimpleUploadedFile(
            "avatar.jpg", avatar_content, content_type="image/jpeg"
        )

        response = self.client.post(
            self.signup_url,
            {
                "username": self.username,
                "password": self.password,
                "avatar": avatar,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "message": "El nombre de usuario ya existe."},
        )
