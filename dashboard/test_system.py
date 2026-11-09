from django.test import TestCase
from django.urls import reverse

from masterdata.factories import make_admin, make_faculty, make_student


class RoleBasedSystemFlowTests(TestCase):
    """Exercise real login, role dashboard access, and logout using the test client."""

    def test_admin_faculty_and_student_can_login_and_open_their_dashboard(self):
        users = [
            make_admin(username="system-admin"),
            make_faculty().user,
            make_student().user,
        ]

        for user in users:
            with self.subTest(role=user.role):
                login_response = self.client.post(
                    reverse("accounts:login"),
                    {"username": user.username, "password": "pass12345"},
                )
                self.assertEqual(login_response.status_code, 302)
                self.assertIn("_auth_user_id", self.client.session)

                dashboard_response = self.client.get(reverse("dashboard:home"))
                self.assertEqual(dashboard_response.status_code, 200)

                logout_response = self.client.post(reverse("accounts:logout"))
                self.assertEqual(logout_response.status_code, 302)
                self.assertNotIn("_auth_user_id", self.client.session)

                protected_response = self.client.get(reverse("dashboard:home"))
                self.assertEqual(protected_response.status_code, 302)
                self.assertIn("/login/", protected_response.url)

    def test_anonymous_user_cannot_open_dashboard(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
