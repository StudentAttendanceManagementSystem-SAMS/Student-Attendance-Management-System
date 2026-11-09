import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from analytics.services import overall_attendance_for_student
from attendance.models import Attendance, AttendanceConfig
from masterdata.factories import make_assignment, make_faculty, make_section, make_student, make_subject


class AttendanceAnalyticsIntegrationTests(TestCase):
    """Exercise the attendance view, database persistence, and analytics service together."""

    def setUp(self):
        self.section = make_section(name="INT-S1-A", semester=1)
        self.subject = make_subject(code="INT101", semester=1)
        self.faculty = make_faculty()
        self.assignment = make_assignment(
            faculty=self.faculty,
            subject=self.subject,
            section=self.section,
        )
        self.student = make_student(section=self.section, semester=1)

        today = timezone.localdate()
        config = AttendanceConfig.get_solo()
        config.term_start_date = today - datetime.timedelta(days=30)
        config.term_end_date = today + datetime.timedelta(days=30)
        config.correction_window_days = 7
        config.save()

        self.url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, today.isoformat()],
        )

    def test_faculty_marks_attendance_and_student_aggregate_reflects_it(self):
        self.client.force_login(self.faculty.user)

        response = self.client.post(
            self.url,
            {f"status_{self.student.pk}": Attendance.PRESENT},
        )

        self.assertEqual(response.status_code, 302)
        record = Attendance.objects.get(
            student=self.student,
            subject=self.subject,
            date=timezone.localdate(),
        )
        self.assertEqual(record.status, Attendance.PRESENT)

        summary = overall_attendance_for_student(self.student)
        self.assertEqual(summary["present_count"], 1)
        self.assertEqual(summary["total_count"], 1)
        self.assertEqual(str(summary["percentage"]), "100.00")

    def test_faculty_cannot_mark_an_unassigned_subject_section(self):
        other_faculty = make_faculty()
        self.client.force_login(other_faculty.user)

        response = self.client.post(
            self.url,
            {f"status_{self.student.pk}": Attendance.PRESENT},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Attendance.objects.filter(
                student=self.student,
                subject=self.subject,
                date=timezone.localdate(),
            ).exists()
        )

    def test_marking_again_updates_the_existing_daily_record(self):
        self.client.force_login(self.faculty.user)
        today = timezone.localdate()

        Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            faculty=self.faculty,
            date=today,
            status=Attendance.ABSENT,
        )

        response = self.client.post(
            self.url,
            {f"status_{self.student.pk}": Attendance.PRESENT},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Attendance.objects.filter(
                student=self.student,
                subject=self.subject,
                date=today,
            ).count(),
            1,
        )
        self.assertEqual(
            Attendance.objects.get(
                student=self.student,
                subject=self.subject,
                date=today,
            ).status,
            Attendance.PRESENT,
        )
