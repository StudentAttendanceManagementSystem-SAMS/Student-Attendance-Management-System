
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
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
        self.assertFormError(
            response.context["form"],
            None,
            "Invalid username or password. Please try again.",
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_repeated_failed_logins_show_warning(self):
        for _ in range(3):
            response = self.client.post(
                self.url,
                {"username": "admin1", "password": "wrong"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            None,
            "Multiple unsuccessful login attempts detected. "
            "Check your credentials carefully before trying again.",
        )

    def test_successful_login_resets_failed_attempt_counter(self):
        self.client.post(self.url, {"username": "admin1", "password": "wrong"})
        self.client.post(self.url, {"username": "admin1", "password": "pass12345"})
        self.assertNotIn("sams_login_failures", self.client.session)


# RBAC decorator tests

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


# Ownership tests

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


# Role-based page access tests

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


# Logout tests

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


# Security tests

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


# Password change tests (SRS FR-AUTH-05)

class PasswordChangeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="password-user",
            password="Old-password-123!",
            role=User.STUDENT,
        )
        self.client.force_login(self.user)
        self.url = reverse("accounts:password_change")

    def test_authenticated_user_can_change_their_password(self):
        response = self.client.post(
            self.url,
            {
                "old_password": "Old-password-123!",
                "new_password1": "New-password-456!",
                "new_password2": "New-password-456!",
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts:password_change_done"),
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("New-password-456!"))
        # PasswordChangeView should preserve the authenticated session.
        self.assertIn("_auth_user_id", self.client.session)

    def test_wrong_old_password_is_rejected(self):
        response = self.client.post(
            self.url,
            {
                "old_password": "incorrect-old-password",
                "new_password1": "New-password-456!",
                "new_password2": "New-password-456!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your old password was entered incorrectly")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Old-password-123!"))

    def test_mismatched_new_passwords_are_rejected(self):
        response = self.client.post(
            self.url,
            {
                "old_password": "Old-password-123!",
                "new_password1": "New-password-456!",
                "new_password2": "Different-password-789!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Old-password-123!"))

    def test_anonymous_user_cannot_open_password_change(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)


class SuperuserRoleInvariantTests(TestCase):
    def test_superuser_role_cannot_be_overridden_to_faculty(self):
        user = User.objects.create_superuser(
            username="forced-admin",
            password="pass12345",
            role=User.FACULTY,
        )

        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, User.ADMIN)


class OwnershipRoleInvariantTests(TestCase):
    def test_admin_does_not_pass_faculty_assignment_ownership(self):
        admin = make_admin()
        faculty = make_faculty()
        assignment = make_assignment(
            faculty,
            make_subject(),
            make_section(),
        )

        self.assertFalse(faculty_owns_assignment(admin, assignment))

    def test_faculty_does_not_pass_student_record_ownership(self):
        faculty = make_faculty()
        student = make_student()

        self.assertFalse(student_owns_record(faculty.user, student))
