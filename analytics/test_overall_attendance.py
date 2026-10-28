import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from attendance.models import Attendance
from masterdata.factories import make_faculty, make_section, make_student, make_subject
from analytics.services import overall_attendance_for_faculty, overall_attendance_for_student


class OverallAttendanceServiceTests(TestCase):
    def setUp(self):
        self.section = make_section(semester=3, name="OVERALL-A")
        self.student = make_student(section=self.section, semester=3)
        self.faculty = make_faculty()
        self.subject_a = make_subject(semester=3, code="OA101")
        self.subject_b = make_subject(semester=3, code="OB101")
        self.other_term_subject = make_subject(semester=4, code="OC201")

    def mark(self, subject, day, status, student=None):
        Attendance.objects.create(
            student=student or self.student,
            subject=subject,
            faculty=self.faculty,
            date=datetime.date(2026, 10, day),
            status=status,
        )

    def test_overall_percentage_is_weighted_by_class_counts(self):
        # Subject A: 3/4 = 75%; Subject B: 1/2 = 50%.
        # Correct aggregate is 4/6 = 66.67%, not the unweighted mean 62.5%.
        for day, status in enumerate(
            [Attendance.PRESENT, Attendance.PRESENT, Attendance.PRESENT, Attendance.ABSENT], 1
        ):
            self.mark(self.subject_a, day, status)
        self.mark(self.subject_b, 5, Attendance.PRESENT)
        self.mark(self.subject_b, 6, Attendance.ABSENT)
        self.mark(self.other_term_subject, 7, Attendance.PRESENT)

        report = overall_attendance_for_student(self.student)

        self.assertEqual(report["semester"], 3)
        self.assertEqual(report["present_count"], 4)
        self.assertEqual(report["total_count"], 6)
        self.assertEqual(report["percentage"], Decimal("66.67"))
        self.assertEqual(len(report["subjects"]), 2)
        self.assertEqual(
            sum(row["present_count"] for row in report["subjects"]),
            report["present_count"],
        )
        self.assertEqual(
            sum(row["total_count"] for row in report["subjects"]),
            report["total_count"],
        )

    def test_no_attendance_returns_none_percentage(self):
        report = overall_attendance_for_student(self.student)
        self.assertIsNone(report["percentage"])
        self.assertEqual(report["total_count"], 0)

    def test_faculty_report_only_includes_assigned_sections(self):
        assigned_student = self.student
        other_section = make_section(semester=3, name="OVERALL-B")
        other_student = make_student(section=other_section, semester=3)
        self.mark(self.subject_a, 1, Attendance.PRESENT, assigned_student)
        self.mark(self.subject_a, 2, Attendance.ABSENT, other_student)
        self.faculty.assignments.create(subject=self.subject_a, section=self.section)

        results = overall_attendance_for_faculty(self.faculty)
        self.assertEqual([row["student"].id for row in results], [assigned_student.id])


class OverallAttendanceViewTests(TestCase):
    def setUp(self):
        self.url = reverse("analytics:overall_attendance")

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_student_can_view_own_overall_attendance(self):
        student = make_student()
        self.client.force_login(student.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "analytics/overall_attendance.html")
        self.assertIn("student_report", response.context)

    def test_faculty_can_view_assigned_section_report(self):
        faculty = make_faculty()
        self.client.force_login(faculty.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("faculty_reports", response.context)

    def test_admin_is_forbidden(self):
        from masterdata.factories import make_admin
        self.client.force_login(make_admin())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
