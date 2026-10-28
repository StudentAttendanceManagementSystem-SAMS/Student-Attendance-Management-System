from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import User
from masterdata.factories import (
    make_admin,
    make_assignment,
    make_faculty,
    make_section,
    make_student,
    make_subject,
)

from .permissions import (
    faculty_owns_assignment,
    role_required,
    student_owns_record,
)

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


class OwnershipTests(TestCase):
    def setUp(self):
        self.faculty = make_faculty()
        self.other_faculty = make_faculty()
        self.assignment = make_assignment(
            self.faculty,
            make_subject(),
            make_section(),
        )
        self.student = make_student()
        self.other_student = make_student()

    def test_faculty_owns_only_their_own_assignment(self):
        self.assertTrue(
            faculty_owns_assignment(self.faculty.user, self.assignment)
        )
        self.assertFalse(
            faculty_owns_assignment(self.other_faculty.user, self.assignment)
        )

    def test_student_account_never_owns_an_assignment(self):
        self.assertFalse(
            faculty_owns_assignment(self.student.user, self.assignment)
        )

    def test_student_owns_only_their_own_record(self):
        self.assertTrue(
            student_owns_record(self.student.user, self.student)
        )
        self.assertFalse(
            student_owns_record(self.student.user, self.other_student)
        )
class RoleAccessTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.faculty = make_faculty()
        self.student = make_student()

        self.assignment = make_assignment(
            self.faculty,
            make_subject(),
            self.student.section,
        )

        self.student_list = reverse("masterdata:student_list")
        self.mark_url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, "2026-10-28"],
        )

    def test_admin_pages_open_for_the_administrator(self):
        self.client.force_login(self.admin)

        response = self.client.get(self.student_list)

        self.assertEqual(response.status_code, 200)

    def test_admin_pages_are_forbidden_for_faculty_and_students(self):
        for user in (self.faculty.user, self.student.user):
            with self.subTest(user=user.username):
                self.client.force_login(user)

                response = self.client.get(self.student_list)

                self.assertEqual(response.status_code, 403)

    def test_faculty_cannot_mark_an_unassigned_section(self):
        self.client.force_login(make_faculty().user)

        response = self.client.get(self.mark_url)

        self.assertEqual(response.status_code, 403)

    def test_assigned_faculty_can_open_the_marking_page(self):
        self.client.force_login(self.faculty.user)

        response = self.client.get(self.mark_url)

        self.assertEqual(response.status_code, 200)

    def test_student_cannot_open_the_marking_page(self):
        self.client.force_login(self.student.user)

        response = self.client.get(self.mark_url)

        self.assertEqual(response.status_code, 403)