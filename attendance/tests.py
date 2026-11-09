import datetime

from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from masterdata.factories import (
    make_admin,
    make_assignment,
    make_faculty,
    make_section,
    make_student,
    make_subject,
)

from .forms import ClassSelectForm
from .models import Attendance, AttendanceConfig


class AttendanceModelTests(TestCase):
    def test_duplicate_student_subject_date_is_rejected(self):
        student = make_student()
        subject = make_subject()
        faculty = make_faculty()
        day = timezone.localdate()

        Attendance.objects.create(
            student=student,
            subject=subject,
            faculty=faculty,
            date=day,
            status=Attendance.PRESENT,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Attendance.objects.create(
                    student=student,
                    subject=subject,
                    faculty=faculty,
                    date=day,
                    status=Attendance.ABSENT,
                )

    def test_default_attendance_configuration(self):
        config = AttendanceConfig.get_solo()
        self.assertEqual(config.pk, 1)
        self.assertEqual(config.threshold_percentage, 75)
        self.assertEqual(config.correction_window_days, 7)

    def test_get_solo_returns_the_same_configuration(self):
        first = AttendanceConfig.get_solo()
        second = AttendanceConfig.get_solo()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(AttendanceConfig.objects.count(), 1)


class AttendanceConfigViewTests(TestCase):
    def setUp(self):
        self.url = reverse("attendance:config")
        self.admin = make_admin()
        self.faculty = make_faculty()

    def test_default_settings_are_displayed_to_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].instance.threshold_percentage,
            75,
        )
        self.assertEqual(
            response.context["form"].instance.correction_window_days,
            7,
        )

    def test_admin_can_update_both_settings(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            self.url,
            {
                "threshold_percentage": 80,
                "correction_window_days": 5,
                "term_start_date": "2026-01-01",
                "term_end_date": "2026-12-31",
            },
        )

        self.assertRedirects(response, self.url)
        config = AttendanceConfig.objects.get(pk=1)
        self.assertEqual(config.threshold_percentage, 80)
        self.assertEqual(config.correction_window_days, 5)
        self.assertEqual(config.term_start_date, datetime.date(2026, 1, 1))
        self.assertEqual(config.term_end_date, datetime.date(2026, 12, 31))

    def test_term_dates_must_be_configured_together_and_in_order(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {
            "threshold_percentage": 75,
            "correction_window_days": 7,
            "term_start_date": "2026-12-31",
            "term_end_date": "2026-01-01",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("term_end_date", response.context["form"].errors)

        response = self.client.post(self.url, {
            "threshold_percentage": 75,
            "correction_window_days": 7,
            "term_start_date": "2026-01-01",
            "term_end_date": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())

    def test_invalid_threshold_is_rejected(self):
        self.client.force_login(self.admin)
        AttendanceConfig.get_solo()

        for value in ("-1", "101"):
            with self.subTest(value=value):
                response = self.client.post(
                    self.url,
                    {
                        "threshold_percentage": value,
                        "correction_window_days": 7,
                        "term_start_date": "2026-01-01",
                        "term_end_date": "2026-12-31",
                    },
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(
                    "threshold_percentage",
                    response.context["form"].errors,
                )
                self.assertEqual(
                    AttendanceConfig.objects.get(pk=1).threshold_percentage,
                    75,
                )

    def test_invalid_correction_window_is_rejected(self):
        self.client.force_login(self.admin)
        AttendanceConfig.get_solo()

        for value in ("-1", "366"):
            with self.subTest(value=value):
                response = self.client.post(
                    self.url,
                    {
                        "threshold_percentage": 75,
                        "correction_window_days": value,
                        "term_start_date": "2026-01-01",
                        "term_end_date": "2026-12-31",
                    },
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(
                    "correction_window_days",
                    response.context["form"].errors,
                )
                self.assertEqual(
                    AttendanceConfig.objects.get(pk=1).correction_window_days,
                    7,
                )

    def test_faculty_cannot_access_threshold_settings(self):
        self.client.force_login(self.faculty.user)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


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
        today = timezone.localdate()
        response = self.client.get(
            self.url,
            {"assignment": self.mine.pk, "date": today.isoformat()},
        )
        self.assertRedirects(
            response,
            reverse(
                "attendance:mark",
                args=[self.mine.pk, today.isoformat()],
            ),
            fetch_redirect_response=False,
        )

    def test_future_date_is_rejected_by_selection_form(self):
        future = timezone.localdate() + datetime.timedelta(days=1)
        form = ClassSelectForm(
            {"assignment": self.mine.pk, "date": future.isoformat()},
            assignments=self.mine.__class__.objects.filter(pk=self.mine.pk),
        )
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_faculty_without_assignments_sees_message(self):
        self.client.force_login(make_faculty().user)
        response = self.client.get(self.url)
        self.assertContains(response, "No classes have been assigned")


class AttendanceRosterTests(TestCase):
    def setUp(self):
        self.section = make_section()
        self.faculty = make_faculty()
        self.assignment = make_assignment(
            self.faculty, make_subject(), self.section
        )
        self.day = timezone.localdate()
        self.url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, self.day.isoformat()],
        )
        self.client.force_login(self.faculty.user)
        AttendanceConfig.objects.update_or_create(
            pk=1,
            defaults={
                "term_start_date": datetime.date(2000, 1, 1),
                "term_end_date": datetime.date(2099, 12, 31),
            },
        )

    def test_roster_lists_every_student_in_the_section(self):
        for _ in range(3):
            make_student(section=self.section)
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["students"]), 3)

    def test_empty_section_shows_message(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No students are enrolled")

    def test_invalid_date_returns_404(self):
        url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, "not-a-date"],
        )
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_future_date_returns_404(self):
        future = timezone.localdate() + datetime.timedelta(days=1)
        url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, future.isoformat()],
        )
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_date_outside_configured_term_is_read_only(self):
        config = AttendanceConfig.get_solo()
        config.term_start_date = self.day + datetime.timedelta(days=1)
        config.term_end_date = self.day + datetime.timedelta(days=30)
        config.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["can_edit"])
        self.assertContains(response, "outside the configured academic term")

    def test_unconfigured_term_blocks_attendance_submission(self):
        AttendanceConfig.objects.all().delete()
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Attendance.objects.count(), 0)

    def test_unassigned_faculty_cannot_open_another_facultys_roster(self):
        other_assignment = make_assignment(
            make_faculty(), make_subject(), self.section
        )
        url = reverse(
            "attendance:mark",
            args=[other_assignment.pk, self.day.isoformat()],
        )
        self.assertEqual(self.client.get(url).status_code, 403)


class SaveAttendanceTests(TestCase):
    def setUp(self):
        self.section = make_section()
        self.faculty = make_faculty()
        self.assignment = make_assignment(
            self.faculty, make_subject(), self.section
        )
        self.students = [
            make_student(section=self.section) for _ in range(3)
        ]
        self.day = timezone.localdate()
        self.url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, self.day.isoformat()],
        )
        self.client.force_login(self.faculty.user)
        AttendanceConfig.objects.update_or_create(
            pk=1,
            defaults={
                "term_start_date": datetime.date(2000, 1, 1),
                "term_end_date": datetime.date(2099, 12, 31),
            },
        )

    def test_post_saves_one_record_per_student(self):
        data = {
            f"status_{student.pk}": Attendance.PRESENT
            for student in self.students
        }
        data[f"status_{self.students[0].pk}"] = Attendance.ABSENT

        response = self.client.post(self.url, data)

        self.assertRedirects(
            response, reverse("attendance:select_class")
        )
        self.assertEqual(Attendance.objects.count(), 3)
        self.assertEqual(
            Attendance.objects.get(student=self.students[0]).status,
            Attendance.ABSENT,
        )

    def test_records_are_linked_to_the_assigned_faculty(self):
        self.client.post(
            self.url,
            {
                f"status_{student.pk}": Attendance.PRESENT
                for student in self.students
            },
        )
        self.assertTrue(
            all(
                record.faculty == self.faculty
                for record in Attendance.objects.all()
            )
        )

    def test_missing_or_invalid_status_defaults_to_absent(self):
        self.client.post(
            self.url,
            {f"status_{self.students[0].pk}": "INVALID"},
        )
        self.assertEqual(Attendance.objects.count(), 3)
        self.assertEqual(
            Attendance.objects.filter(status=Attendance.ABSENT).count(),
            3,
        )

    def test_second_submission_updates_existing_records(self):
        present = {
            f"status_{student.pk}": Attendance.PRESENT
            for student in self.students
        }
        absent = {
            f"status_{student.pk}": Attendance.ABSENT
            for student in self.students
        }
        self.client.post(self.url, present)
        self.client.post(self.url, absent)

        self.assertEqual(Attendance.objects.count(), 3)
        self.assertEqual(
            Attendance.objects.filter(status=Attendance.ABSENT).count(),
            3,
        )

    def test_existing_values_are_shown_when_reopened(self):
        data = {
            f"status_{student.pk}": Attendance.PRESENT
            for student in self.students
        }
        data[f"status_{self.students[1].pk}"] = Attendance.ABSENT
        self.client.post(self.url, data)

        response = self.client.get(self.url)
        self.assertContains(
            response,
            f'name="status_{self.students[1].pk}"',
        )
        self.assertContains(response, "editing the existing records")

    def test_edit_is_allowed_on_correction_window_boundary(self):
        config = AttendanceConfig.get_solo()
        config.correction_window_days = 7
        config.save()
        day = timezone.localdate() - datetime.timedelta(days=7)
        student = self.students[0]
        Attendance.objects.create(
            student=student,
            subject=self.assignment.subject,
            faculty=self.faculty,
            date=day,
            status=Attendance.PRESENT,
        )
        url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, day.isoformat()],
        )

        response = self.client.post(
            url, {f"status_{student.pk}": Attendance.ABSENT}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Attendance.objects.get(student=student, date=day).status,
            Attendance.ABSENT,
        )

    def test_expired_attendance_is_read_only_and_cannot_be_posted(self):
        config = AttendanceConfig.get_solo()
        config.correction_window_days = 7
        config.save()
        old_day = timezone.localdate() - datetime.timedelta(days=8)
        student = self.students[0]
        Attendance.objects.create(
            student=student,
            subject=self.assignment.subject,
            faculty=self.faculty,
            date=old_day,
            status=Attendance.PRESENT,
        )
        url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, old_day.isoformat()],
        )

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)
        self.assertFalse(get_response.context["can_edit"])
        self.assertContains(get_response, "viewing only")

        post_response = self.client.post(
            url, {f"status_{student.pk}": Attendance.ABSENT}
        )
        self.assertEqual(post_response.status_code, 403)
        self.assertEqual(
            Attendance.objects.get(student=student, date=old_day).status,
            Attendance.PRESENT,
        )

    def test_marking_one_subject_does_not_touch_another(self):
        other_assignment = make_assignment(
            self.faculty, make_subject(), self.section
        )
        self.client.post(
            self.url,
            {
                f"status_{self.students[0].pk}": Attendance.PRESENT,
            },
        )

        # The attendance view saves one status for every student in the
        # selected section. Missing statuses default to Absent.
        self.assertEqual(
            Attendance.objects.filter(subject=self.assignment.subject).count(),
            len(self.students),
        )
        self.assertFalse(
            Attendance.objects.filter(subject=other_assignment.subject).exists()
        )

        other_url = reverse(
            "attendance:mark",
            args=[other_assignment.pk, self.day.isoformat()],
        )
        self.client.post(
            other_url,
            {
                f"status_{self.students[0].pk}": Attendance.ABSENT,
            },
        )

        self.assertEqual(Attendance.objects.count(), len(self.students) * 2)
        self.assertEqual(
            Attendance.objects.filter(subject=self.assignment.subject).count(),
            len(self.students),
        )
        self.assertEqual(
            Attendance.objects.filter(subject=other_assignment.subject).count(),
            len(self.students),
        )
        self.assertEqual(
            Attendance.objects.get(
                student=self.students[0], subject=self.assignment.subject
            ).status,
            Attendance.PRESENT,
        )
        self.assertEqual(
            Attendance.objects.get(
                student=self.students[0], subject=other_assignment.subject
            ).status,
            Attendance.ABSENT,
        )
