from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse

from .models import User


class UserRoleTests(TestCase):
    def test_user_is_saved_with_a_role(self):
        user = User.objects.create_user(
            username="fac1",
            password="pass12345",
            role=User.FACULTY,
        )
        self.assertEqual(user.role, "FACULTY")

    def test_role_is_required(self):
        with self.assertRaises(ValidationError) as ctx:
            User(username="norole").full_clean()
        self.assertIn("role", ctx.exception.message_dict)

    def test_invalid_role_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username="bad",
                    password="pass12345",
                    role="BOSS",
                )

    def test_superuser_gets_administrator_role(self):
        user = User.objects.create_superuser(
            username="root",
            password="pass12345",
        )
        self.assertEqual(user.role, User.ADMIN)

class LoginTests(TestCase):
    def setUp(self):
        User.objects.create_user(
            username="admin1",
            password="pass12345",
            role=User.ADMIN,
        )
        self.url = reverse("accounts:login")

    def test_valid_login_creates_session(self):
        response = self.client.post(
            self.url,
            {"username": "admin1", "password": "pass12345"},
        )
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            fetch_redirect_response=False,
        )
        self.assertIn("_auth_user_id", self.client.session)

    def test_invalid_login_shows_error_and_creates_no_session(self):
        response = self.client.post(
            self.url,
            {"username": "admin1", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")
        self.assertNotIn("_auth_user_id", self.client.session)


class LogoutTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username="fac1",
            password="pass12345",
            role=User.FACULTY,
        )
        self.client.force_login(user)

    def test_logout_ends_the_session(self):
        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_protected_page_redirects_to_login_after_logout(self):
        self.client.post(reverse("accounts:logout"))

        home = reverse("accounts:home")
        response = self.client.get(home)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={home}",
        )

    def test_session_expires_after_two_hours_of_inactivity(self):
        self.assertEqual(settings.SESSION_COOKIE_AGE, 7200)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)

class SecurityTests(TestCase):
    def test_anonymous_users_are_redirected_to_login(self):
        urls = [
            reverse("accounts:home"),
            reverse("masterdata:student_list"),
            reverse("attendance:select_class"),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f"{reverse('accounts:login')}?next={url}",
                    fetch_redirect_response=False,
                )

    def test_login_page_stays_public(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)

    def test_post_without_csrf_token_is_rejected(self):
        strict = Client(enforce_csrf_checks=True)

        response = strict.post(
            reverse("accounts:login"),
            {"username": "a", "password": "b"},
        )

        self.assertEqual(response.status_code, 403)

    def test_passwords_are_stored_hashed(self):
        user = User.objects.create_user(
            username="h1",
            password="plain-pass-123",
            role=User.STUDENT,
        )

        self.assertNotEqual(user.password, "plain-pass-123")
        self.assertIn("$", user.password)
        self.assertTrue(user.check_password("plain-pass-123"))
