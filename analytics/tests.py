import datetime
from decimal import Decimal

from django.test import SimpleTestCase, TestCase

from attendance.models import Attendance
from masterdata.factories import (
    make_faculty,
    make_section,
    make_student,
    make_subject,
)

from .services import percentage, section_wise_report, subject_wise_report


class PercentageTests(SimpleTestCase):
    def test_calculates_percentage(self):
        self.assertEqual(percentage(3, 4), Decimal("75.00"))

    def test_returns_none_when_no_classes_were_recorded(self):
        self.assertIsNone(percentage(0, 0))

    def test_rounds_to_two_decimal_places(self):
        self.assertEqual(percentage(2, 3), Decimal("66.67"))


class SectionWiseReportTests(TestCase):
    def setUp(self):
        self.section_a = make_section(name="CSE-REPORT-A")
        self.section_b = make_section(name="CSE-REPORT-B")

        self.student_a1 = make_student(section=self.section_a)
        self.student_a2 = make_student(section=self.section_a)
        self.student_b1 = make_student(section=self.section_b)

        self.subject = make_subject()
        self.faculty = make_faculty()

    def mark(self, student, day, status):
        Attendance.objects.create(
            student=student,
            subject=self.subject,
            faculty=self.faculty,
            date=datetime.date(2026, 10, day),
            status=status,
        )

    def test_report_calculates_each_section_separately(self):
        self.mark(self.student_a1, 1, Attendance.PRESENT)
        self.mark(self.student_a1, 2, Attendance.ABSENT)
        self.mark(self.student_a2, 1, Attendance.PRESENT)
        self.mark(self.student_b1, 1, Attendance.ABSENT)

        report = {
            row["section"].name: row
            for row in section_wise_report()
        }

        section_a = report["CSE-REPORT-A"]
        self.assertEqual(section_a["student_count"], 2)
        self.assertEqual(section_a["total_records"], 3)
        self.assertEqual(section_a["present_count"], 2)
        self.assertEqual(section_a["absent_count"], 1)
        self.assertEqual(section_a["percentage"], Decimal("66.67"))

        section_b = report["CSE-REPORT-B"]
        self.assertEqual(section_b["student_count"], 1)
        self.assertEqual(section_b["total_records"], 1)
        self.assertEqual(section_b["present_count"], 0)
        self.assertEqual(section_b["absent_count"], 1)
        self.assertEqual(section_b["percentage"], Decimal("0.00"))

    def test_section_without_attendance_returns_none_percentage(self):
        report = {
            row["section"].name: row
            for row in section_wise_report()
        }

        section_b = report["CSE-REPORT-B"]

        self.assertEqual(section_b["student_count"], 1)
        self.assertEqual(section_b["total_records"], 0)
        self.assertIsNone(section_b["percentage"])


class SubjectWiseReportTests(TestCase):
    def setUp(self):
        section_a = make_section(name="CSE-SUBJECT-A")
        section_b = make_section(name="CSE-SUBJECT-B")

        self.student_a1 = make_student(section=section_a)
        self.student_a2 = make_student(section=section_a)
        self.student_b1 = make_student(section=section_b)

        self.subject = make_subject()
        self.faculty = make_faculty()

    def mark(self, student, day, status):
        Attendance.objects.create(
            student=student,
            subject=self.subject,
            faculty=self.faculty,
            date=datetime.date(2026, 10, day),
            status=status,
        )

    def test_subject_report_aggregates_across_sections(self):
        self.mark(self.student_a1, 1, Attendance.PRESENT)
        self.mark(self.student_a2, 1, Attendance.ABSENT)
        self.mark(self.student_b1, 1, Attendance.PRESENT)

        report = subject_wise_report()

        self.assertEqual(len(report), 1)

        row = report[0]
        self.assertEqual(row["sections_with_records"], 2)
        self.assertEqual(row["students_with_records"], 3)
        self.assertEqual(row["total_records"], 3)
        self.assertEqual(row["present_count"], 2)
        self.assertEqual(row["absent_count"], 1)
        self.assertEqual(row["percentage"], Decimal("66.67"))

    def test_subject_without_attendance_returns_none_percentage(self):
        row = subject_wise_report()[0]

        self.assertEqual(row["total_records"], 0)
        self.assertIsNone(row["percentage"])

class ReportViewTests(TestCase):
    def test_admin_can_open_both_report_pages(self):
        from django.urls import reverse
        from masterdata.factories import make_admin

        self.client.force_login(make_admin())

        response = self.client.get(reverse("analytics:section_report"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Section-wise Attendance Report")

        response = self.client.get(reverse("analytics:subject_report"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Subject-wise Attendance Report")

    def test_faculty_and_students_cannot_open_report_pages(self):
        from django.urls import reverse

        users = [make_faculty().user, make_student().user]
        routes = [
            "analytics:section_report",
            "analytics:subject_report",
        ]

        for user in users:
            self.client.force_login(user)

            for route in routes:
                with self.subTest(user=user.username, route=route):
                    response = self.client.get(reverse(route))
                    self.assertEqual(response.status_code, 403)

    def test_anonymous_users_are_redirected_to_login(self):
        from django.urls import reverse

        for route in [
            "analytics:section_report",
            "analytics:subject_report",
        ]:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 302)
