from allauth.socialaccount.models import SocialApp
from base import mods
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from .forms import LoginForm, RegisterForm


class AuthTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(username="voter1")
        u.set_password("123")
        u.save()

        u2 = User(username="admin")
        u2.set_password("admin")
        u2.is_superuser = True
        u2.save()

    def tearDown(self):
        self.client = None

    def test_login(self):
        data = {"username": "voter1", "password": "123"}
        response = self.client.post("/authentication/login/", data, format="json")
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get("token"))

    def test_login_fail(self):
        data = {"username": "voter1", "password": "321"}
        response = self.client.post("/authentication/login/", data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
        data = {"username": "voter1", "password": "123"}
        response = self.client.post("/authentication/login/", data, format="json")
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post("/authentication/getuser/", token, format="json")
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user["id"], 1)
        self.assertEqual(user["username"], "voter1")

    def test_getuser_invented_token(self):
        token = {"token": "invented"}
        response = self.client.post("/authentication/getuser/", token, format="json")
        self.assertEqual(response.status_code, 404)


class LogoutViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("signin")
        self.user = User.objects.create_user(username="testuser", password="testpass")
        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test",
            secret="test",
        )
        # Add the current site to the SocialApp's sites
        app.sites.add(Site.objects.get_current())

    def test_logout(self):
        data = {"username": "testuser", "password": "testpass", "remember_me": False}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        response = self.client.get("/authentication/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        response = self.client.get("/authentication/logout/")
        self.assertEqual(response.status_code, 302)


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("signin")
        self.user = User.objects.create_user(username="testuser", password="testpass")
        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test",
            secret="test",
        )
        # Add the current site to the SocialApp's sites
        app.sites.add(Site.objects.get_current())

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authentication/login.html")
        self.assertIsInstance(response.context["form"], LoginForm)
        self.assertIsNone(response.context["msg"])

    def test_post_valid_credentials(self):
        data = {"username": "testuser", "password": "testpass", "remember_me": False}
        response = self.client.post(self.url, data)
        self.assertRedirects(response, "/")

    def test_post_invalid_credentials(self):
        data = {"username": "testuser", "password": "wrongpass", "remember_me": False}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authentication/login.html")
        self.assertIsInstance(response.context["form"], LoginForm)
        self.assertEqual(response.context["msg"], "Credenciales incorrectas")

    def test_post_invalid_form(self):
        data = {"username": "", "password": "", "remember_me": False}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authentication/login.html")
        self.assertIsInstance(response.context["form"], LoginForm)
        self.assertEqual(response.context["msg"], "Error en el formulario")


class RegisterViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("register")
        app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test",
            secret="test",
        )
        # Add the current site to the SocialApp's sites
        app.sites.add(Site.objects.get_current())

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authentication/register.html")
        self.assertIsInstance(response.context["form"], RegisterForm)
        self.assertIsNone(response.context["msg"])

    def test_post_valid_form(self):
        data = {
            "username": "new_user",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password1": "strong_password123",
            "password2": "strong_password123",
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertTrue(User.objects.filter(username=data["username"]).exists())
        self.assertRedirects(response, "/signin/")

    def test_post_invalid_form(self):
        data = {
            "username": "bad_user",
            "first_name": "",
            "last_name": "",
            "email": "invalid_email",
            "password1": "password",
            "password2": "password_mismatch",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authentication/register.html")
        self.assertIsInstance(response.context["form"], RegisterForm)
        self.assertIn("form", response.context)
        self.assertTrue(response.context["form"].errors)

    def test_post_user_already_exists(self):
        User.objects.create_user(
            username="existing_user",
            email="existing_user@example.com",
            password="existing_password",
        )
        data = {
            "username": "existing_user",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password1": "strong_password123",
            "password2": "strong_password123",
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertIn(
            "Ya existe un usuario con este nombre.",
            response.context["form"].errors["username"],
        )


class ChangePasswordViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="passuser", password="testpass")
        self.client.force_login(self.user)
        self.url = reverse("change-password")

    def test_change_password_view_success(self):
        response = self.client.post(
            self.url,
            {
                "old_password": "testpass",
                "new_password1": "newtestpass",
                "new_password2": "newtestpass",
            },
        )
        self.assertRedirects(response, expected_url="/")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newtestpass"))

    def test_change_password_view_failure(self):
        response = self.client.post(
            self.url,
            {
                "old_password": "wrongpass",
                "new_password1": "newtestpass",
                "new_password2": "newtestpass",
            },
        )
        self.assertIn(
            "Su contraseña antigua es incorrecta. Por favor, vuelva a introducirla. ",
            response.context["form"].errors["old_password"],
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("testpass"))
