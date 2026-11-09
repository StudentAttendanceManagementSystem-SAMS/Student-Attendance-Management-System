import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from attendance.models import Attendance
from masterdata.factories import make_admin, make_faculty, make_section, make_student, make_subject

from .services import (
    below_threshold_students,
    faculty_subject_report,
    section_wise_report,
    student_attendance_history,
    subject_wise_report,
)


class AnalyticsEnhancementTests(TestCase):
    def setUp(self):
        self.section = make_section(name="ANALYTICS-ENH-A", semester=3)
        self.other_section = make_section(name="ANALYTICS-ENH-B", semester=3)
        self.student = make_student(section=self.section, semester=3)
        self.other_student = make_student(section=self.other_section, semester=3)
        self.faculty = make_faculty()
        self.subject = make_subject(code="ANL301", semester=3)
        self.other_subject = make_subject(code="ANL302", semester=3)

    def mark(self, student, subject, day, status):
        return Attendance.objects.create(
            student=student,
            subject=subject,
            faculty=self.faculty,
            date=datetime.date(2026, 10, day),
            status=status,
        )

    def test_date_range_filters_section_and_subject_reports(self):
        self.mark(self.student, self.subject, 1, Attendance.PRESENT)
        self.mark(self.student, self.subject, 2, Attendance.ABSENT)
        self.mark(self.other_student, self.subject, 3, Attendance.PRESENT)

        section_rows = {
            row["section"].pk: row
            for row in section_wise_report(
                datetime.date(2026, 10, 1), datetime.date(2026, 10, 2)
            )
        }
        self.assertEqual(section_rows[self.section.pk]["total_records"], 2)
        self.assertEqual(section_rows[self.other_section.pk]["total_records"], 0)

        subject_rows = subject_wise_report(
            datetime.date(2026, 10, 1), datetime.date(2026, 10, 2)
        )
        row = next(item for item in subject_rows if item["subject"].pk == self.subject.pk)
        self.assertEqual(row["total_records"], 2)
        self.assertEqual(row["percentage"], Decimal("50.00"))

    def test_faculty_subject_report_requires_exact_assignment(self):
        self.mark(self.student, self.subject, 1, Attendance.PRESENT)
        self.faculty.assignments.create(subject=self.subject, section=self.section)

        report = faculty_subject_report(self.faculty, self.section.pk, self.subject.pk)
        self.assertIsNotNone(report)
        self.assertEqual(len(report["rows"]), 1)
        self.assertEqual(report["rows"][0]["percentage"], Decimal("100.00"))

        denied_report = faculty_subject_report(
            self.faculty, self.other_section.pk, self.subject.pk
        )
        self.assertIsNone(denied_report)

    def test_student_history_can_be_filtered_by_subject_and_dates(self):
        first = self.mark(self.student, self.subject, 1, Attendance.PRESENT)
        self.mark(self.student, self.subject, 2, Attendance.ABSENT)
        self.mark(self.student, self.other_subject, 2, Attendance.PRESENT)

        history = student_attendance_history(
            self.student,
            subject_id=self.subject.pk,
            date_from=datetime.date(2026, 10, 1),
            date_to=datetime.date(2026, 10, 1),
        )
        self.assertEqual(list(history), [first])

    def test_below_threshold_includes_subject_level_result(self):
        # Overall can be above threshold while one subject is below it.
        for day in range(1, 11):
            self.mark(
                self.student,
                self.subject,
                day,
                Attendance.PRESENT if day <= 6 else Attendance.ABSENT,
            )
        for day in range(11, 21):
            self.mark(self.student, self.other_subject, day, Attendance.PRESENT)

        result = next(
            item for item in below_threshold_students()
            if item["student"].pk == self.student.pk
        )
        self.assertFalse(result["overall_below"])
        self.assertEqual([row["subject"].pk for row in result["subject_results"]], [self.subject.pk])

    def test_faculty_subject_report_page_is_role_protected(self):
        self.client.force_login(make_admin())
        response = self.client.get(reverse("analytics:faculty_subject_report"))
        self.assertEqual(response.status_code, 403)

    def test_student_history_page_only_shows_own_records(self):
        self.mark(self.student, self.subject, 1, Attendance.PRESENT)
        self.mark(self.other_student, self.subject, 1, Attendance.ABSENT)
        self.client.force_login(self.student.user)

        response = self.client.get(reverse("analytics:my_attendance_history"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["records"].values_list("student_id", flat=True)), [self.student.pk])

    def test_admin_can_open_student_history(self):
        self.client.force_login(make_admin())
        response = self.client.get(
            reverse("analytics:student_attendance_history", args=[self.student.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_admin_cannot_use_student_self_history_route(self):
        self.client.force_login(make_admin())
        response = self.client.get(reverse("analytics:my_attendance_history"))
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_request_another_students_history_by_id(self):
        self.client.force_login(self.student.user)
        response = self.client.get(
            reverse("analytics:student_attendance_history", args=[self.other_student.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_faculty_history_requires_an_assigned_subject(self):
        self.faculty.assignments.create(
            subject=self.subject,
            section=self.section,
        )
        self.client.force_login(self.faculty.user)
        response = self.client.get(
            reverse("analytics:student_attendance_history", args=[self.student.pk]),
            {"subject": self.other_subject.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["filter_form"].is_valid())
        self.assertEqual(list(response.context["records"]), [])

    def test_invalid_subject_filter_does_not_raise_server_error(self):
        self.client.force_login(self.student.user)
        response = self.client.get(
            reverse("analytics:my_attendance_history"),
            {"subject": "not-a-number"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["filter_form"].is_valid())
