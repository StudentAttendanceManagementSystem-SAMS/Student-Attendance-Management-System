from django.db import IntegrityError, transaction
from django.test import TestCase

from masterdata.factories import make_faculty, make_student, make_subject

from .models import Attendance, AttendanceConfig


class AttendanceModelTests(TestCase):
    def test_duplicate_student_subject_date_is_rejected(self):
        student, subject, faculty = make_student(), make_subject(), make_faculty()
        Attendance.objects.create(
            student=student, subject=subject, faculty=faculty, date="2026-10-21", status=Attendance.PRESENT
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Attendance.objects.create(
                    student=student, subject=subject, faculty=faculty, date="2026-10-21", status=Attendance.ABSENT
                )

    def test_default_threshold_is_75(self):
        self.assertEqual(AttendanceConfig.objects.create().threshold_percentage, 75)
