from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import User
from .permissions import role_required

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

@role_required(User.ADMIN)
def admin_only_view(request):
    return HttpResponse("ok")


class RoleRequiredTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def make_request(self, user):
        request = self.factory.get("/protected/")
        request.user = user
        return request

    def test_anonymous_user_is_redirected_to_login(self):
        response = admin_only_view(
            self.make_request(AnonymousUser())
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_wrong_role_is_forbidden(self):
        with self.assertRaises(PermissionDenied):
            admin_only_view(
                self.make_request(
                    User(username="s", role=User.STUDENT)
                )
            )

    def test_correct_role_is_allowed(self):
        response = admin_only_view(
            self.make_request(
                User(username="a", role=User.ADMIN)
            )
        )
        self.assertEqual(response.status_code, 200)