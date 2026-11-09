import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from attendance.models import Attendance, AttendanceConfig
from masterdata.factories import (
    make_admin,
    make_assignment,
    make_faculty,
    make_section,
    make_student,
    make_subject,
)


class RoleDashboardTests(TestCase):
    def setUp(self):
        self.url = reverse("dashboard:home")
        self.section = make_section(name="DASH-3A", semester=3)
        self.subject = make_subject(code="DASH301", semester=3)
        self.faculty = make_faculty()
        self.assignment = make_assignment(
            self.faculty, self.subject, self.section
        )
        self.student = make_student(section=self.section, semester=3)
        self.config = AttendanceConfig.get_solo()
        self.config.threshold_percentage = 75
        self.config.save()

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_admin_dashboard_contains_institution_counts(self):
        admin = make_admin()
        self.client.force_login(admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["student_count"], 1)
        self.assertEqual(response.context["faculty_count"], 1)
        self.assertEqual(response.context["section_count"], 1)
        self.assertEqual(response.context["subject_count"], 1)

    def test_faculty_dashboard_shows_assignment_and_todays_status(self):
        self.client.force_login(self.faculty.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["assignment_count"], 1)
        self.assertFalse(response.context["assignments"][0]["marked_today"])

        Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            faculty=self.faculty,
            date=timezone.localdate(),
            status=Attendance.PRESENT,
        )
        response = self.client.get(self.url)
        self.assertTrue(response.context["assignments"][0]["marked_today"])

    def test_student_dashboard_shows_only_own_summary(self):
        Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            faculty=self.faculty,
            date=datetime.date(2026, 11, 1),
            status=Attendance.PRESENT,
        )
        self.client.force_login(self.student.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["report"]["percentage"], Decimal("100.00"))
        self.assertEqual(response.context["student"].pk, self.student.pk)

    def test_dashboard_route_rejects_unknown_role(self):
        user = User.objects.create_user(
            username="faculty-without-profile",
            password="pass12345",
            role=User.FACULTY,
        )
        self.client.force_login(user)
        self.assertEqual(self.client.get(self.url).status_code, 403)
