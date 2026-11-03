
import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from attendance.models import Attendance, AttendanceConfig
from analytics.services import below_threshold_students
from masterdata.factories import (
    make_admin,
    make_faculty,
    make_section,
    make_student,
    make_subject,
)


class BelowThresholdServiceTests(TestCase):
    def setUp(self):
        config = AttendanceConfig.get_solo()
        config.threshold_percentage = 75
        config.save()

        self.section = make_section()
        self.subject = make_subject()
        self.faculty = make_faculty()

        self.below_student = make_student(section=self.section)
        self.exact_student = make_student(section=self.section)
        self.above_student = make_student(section=self.section)
        self.no_records_student = make_student(section=self.section)

    def mark_attendance(self, student, present, total):
        for day in range(1, total + 1):
            status = (
                Attendance.PRESENT
                if day <= present
                else Attendance.ABSENT
            )

            Attendance.objects.create(
                student=student,
                subject=self.subject,
                faculty=self.faculty,
                date=datetime.date(2026, 10, day),
                status=status,
            )

    def test_identifies_students_below_threshold(self):
        self.mark_attendance(self.below_student, 6, 10)
        self.mark_attendance(self.exact_student, 6, 8)
        self.mark_attendance(self.above_student, 8, 10)

        results = below_threshold_students()
        result_by_student = {
            item["student"].id: item for item in results
        }

        self.assertIn(self.below_student.id, result_by_student)
        self.assertNotIn(self.exact_student.id, result_by_student)
        self.assertNotIn(self.above_student.id, result_by_student)
        self.assertNotIn(self.no_records_student.id, result_by_student)

        row = result_by_student[self.below_student.id]

        self.assertEqual(row["present_count"], 6)
        self.assertEqual(row["total_count"], 10)
        self.assertEqual(row["percentage"], Decimal("60.00"))
        self.assertEqual(row["threshold"], 75)

    def test_student_exactly_at_threshold_is_excluded(self):
        self.mark_attendance(self.exact_student, 6, 8)

        results = below_threshold_students()

        self.assertFalse(
            any(
                item["student"].id == self.exact_student.id
                for item in results
            )
        )

    def test_student_without_attendance_is_excluded(self):
        results = below_threshold_students()

        self.assertFalse(
            any(
                item["student"].id == self.no_records_student.id
                for item in results
            )
        )


class BelowThresholdViewTests(TestCase):
    def setUp(self):
        config = AttendanceConfig.get_solo()
        config.threshold_percentage = 75
        config.save()

        self.url = reverse("analytics:below_threshold")

        self.section_a = make_section()
        self.section_b = make_section()
        self.subject = make_subject()
        self.faculty_profile = make_faculty()

        self.low_student_a = make_student(section=self.section_a)
        self.low_student_b = make_student(section=self.section_b)

        self.mark_low_attendance(self.low_student_a)
        self.mark_low_attendance(self.low_student_b)

    def mark_low_attendance(self, student):
        for day in range(1, 11):
            status = (
                Attendance.PRESENT
                if day <= 6
                else Attendance.ABSENT
            )

            Attendance.objects.create(
                student=student,
                subject=self.subject,
                faculty=self.faculty_profile,
                date=datetime.date(2026, 10, day),
                status=status,
            )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_administrator_can_view_below_threshold_students(self):
        admin = make_admin()
        self.client.force_login(admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "analytics/below_threshold.html",
        )

        student_ids = {
            item["student"].id
            for item in response.context["students"]
        }

        self.assertIn(self.low_student_a.id, student_ids)
        self.assertIn(self.low_student_b.id, student_ids)

    def test_student_role_is_forbidden(self):
        student = self.low_student_a.user
        self.client.force_login(student)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_faculty_sees_only_assigned_sections(self):
        self.faculty_profile.assignments.create(
            subject=self.subject,
            section=self.section_a,
        )
        self.client.force_login(self.faculty_profile.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        student_ids = {
            item["student"].id
            for item in response.context["students"]
        }

        self.assertIn(self.low_student_a.id, student_ids)
        self.assertNotIn(self.low_student_b.id, student_ids)
