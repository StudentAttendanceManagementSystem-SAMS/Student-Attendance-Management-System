from django.db import IntegrityError, transaction
from django.test import TestCase

from masterdata.factories import make_faculty, make_student, make_subject

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from masterdata.factories import (
    make_assignment,
    make_faculty,
    make_section,
    make_student,
    make_subject,
)

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
        student = make_student()
        subject = make_subject()
        faculty = make_faculty()

        Attendance.objects.create(
            student=student,
            subject=subject,
            faculty=faculty,
            date="2026-10-21",
            status=Attendance.PRESENT,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Attendance.objects.create(
                    student=student,
                    subject=subject,
                    faculty=faculty,
                    date="2026-10-21",
                    status=Attendance.ABSENT,
                )

    def test_default_threshold_is_75(self):
        config = AttendanceConfig.objects.create()
        self.assertEqual(config.threshold_percentage, 75)


class ClassSelectionTests(TestCase):
    def setUp(self):
        self.section = make_section()
        self.faculty = make_faculty()
        self.other_faculty = make_faculty()

        self.mine = make_assignment(
            self.faculty, make_subject(), self.section
        )
        self.theirs = make_assignment(
            self.other_faculty, make_subject(), self.section
        )

        self.client.force_login(self.faculty.user)
        self.url = reverse("attendance:select_class")

    def test_only_own_assignments_are_listed(self):
        response = self.client.get(self.url)
        queryset = response.context["form"].fields["assignment"].queryset

        self.assertEqual(list(queryset), [self.mine])

    def test_valid_selection_redirects_to_roster(self):
        response = self.client.get(
            self.url,
            {"assignment": self.mine.pk, "date": "2026-10-22"},
        )

        self.assertRedirects(
            response,
            reverse(
                "attendance:mark",
                args=[self.mine.pk, "2026-10-22"],
            ),
            fetch_redirect_response=False,
        )

    def test_faculty_without_assignments_sees_message(self):
        self.client.force_login(make_faculty().user)
        response = self.client.get(self.url)

        self.assertContains(response, "No classes have been assigned")
