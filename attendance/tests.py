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
import datetime

from attendance.models import Attendance, AttendanceConfig



class AttendanceModelTests(TestCase):
    def test_duplicate_student_subject_date_is_rejected(self):
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


class RosterViewTests(TestCase):
    def setUp(self):
        self.section = make_section()
        self.faculty = make_faculty()
        self.assignment = make_assignment(
            self.faculty, make_subject(), self.section
        )
        self.client.force_login(self.faculty.user)
        self.url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, "2026-10-26"],
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
        self.client.force_login(self.faculty.user)
        self.url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, "2026-10-27"],
        )

    def test_post_saves_one_record_per_student(self):
        data = {f"status_{student.pk}": "P" for student in self.students}
        data[f"status_{self.students[0].pk}"] = "A"

        response = self.client.post(self.url, data)

        self.assertRedirects(
            response, reverse("attendance:select_class")
        )
        self.assertEqual(Attendance.objects.count(), 3)
        self.assertEqual(
            Attendance.objects.get(student=self.students[0]).status, "A"
        )

    def test_records_are_linked_to_the_faculty_member(self):
        self.client.post(
            self.url,
            {f"status_{student.pk}": "P" for student in self.students},
        )

        self.assertTrue(
            all(
                record.faculty == self.faculty
                for record in Attendance.objects.all()
            )
        )

    def test_missing_status_defaults_to_absent(self):
        self.client.post(self.url, {})
        self.assertEqual(
            Attendance.objects.filter(status=Attendance.ABSENT).count(), 3
        )
        
class DuplicateMarkingTests(TestCase):
    def setUp(self):
        self.section = make_section()
        self.faculty = make_faculty()
        self.assignment = make_assignment(self.faculty, make_subject(), self.section)
        self.students = [make_student(section=self.section) for _ in range(3)]
        self.client.force_login(self.faculty.user)
        self.url = reverse("attendance:mark", args=[self.assignment.pk, "2026-10-28"])

    def test_second_submission_updates_instead_of_duplicating(self):
        self.client.post(self.url, {f"status_{s.pk}": "P" for s in self.students})
        self.client.post(self.url, {f"status_{s.pk}": "A" for s in self.students})
        self.assertEqual(Attendance.objects.count(), 3)
        self.assertEqual(Attendance.objects.filter(status="A").count(), 3)

    def test_existing_values_are_shown_when_reopened(self):
        data = {f"status_{s.pk}": "P" for s in self.students}
        data[f"status_{self.students[1].pk}"] = "A"
        self.client.post(self.url, data)
        response = self.client.get(self.url)
        self.assertContains(response, f'name="status_{self.students[1].pk}" value="A" checked')
        self.assertContains(response, "already exists")
        
class AttendanceCorrectionWindowTests(TestCase):
    def setUp(self):
        self.section = make_section()
        self.faculty = make_faculty()
        self.subject = make_subject(semester=self.section.semester)
        self.assignment = make_assignment(self.faculty, self.subject, self.section)
        self.student = make_student(section=self.section, semester=self.section.semester)
        self.client.force_login(self.faculty.user)
        self.config = AttendanceConfig.get_solo()
        self.config.correction_window_days = 1
        self.config.save()
        self.today = datetime.date.today()

    def url_for(self, day):
        return reverse(
            "attendance:mark",
            args=[self.assignment.pk, day.isoformat()],
        )

    def test_same_day_attendance_can_be_created(self):
        response = self.client.post(
            self.url_for(self.today),
            {f"status_{self.student.pk}": Attendance.PRESENT},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Attendance.objects.get().status, Attendance.PRESENT)

    def test_yesterdays_attendance_can_be_corrected_with_one_day_window(self):
        yesterday = self.today - datetime.timedelta(days=1)
        Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            faculty=self.faculty,
            date=yesterday,
            status=Attendance.ABSENT,
        )
        response = self.client.post(
            self.url_for(yesterday),
            {f"status_{self.student.pk}": Attendance.PRESENT},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Attendance.objects.get().status, Attendance.PRESENT)

    def test_expired_correction_is_rejected(self):
        old_day = self.today - datetime.timedelta(days=3)
        Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            faculty=self.faculty,
            date=old_day,
            status=Attendance.ABSENT,
        )
        response = self.client.post(
            self.url_for(old_day),
            {f"status_{self.student.pk}": Attendance.PRESENT},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Attendance.objects.get().status, Attendance.ABSENT)

    def test_future_attendance_is_rejected(self):
        future_day = self.today + datetime.timedelta(days=1)
        response = self.client.post(
            self.url_for(future_day),
            {f"status_{self.student.pk}": Attendance.PRESENT},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Attendance.objects.exists())
