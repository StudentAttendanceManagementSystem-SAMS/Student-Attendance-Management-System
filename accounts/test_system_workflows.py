import datetime

from django.test import TestCase
from django.urls import reverse

from attendance.models import Attendance, AttendanceConfig
from masterdata.factories import (
    make_admin,
    make_assignment,
    make_faculty,
    make_section,
    make_student,
    make_subject,
)


class SamsRoleWorkflowTests(TestCase):

    def setUp(self):
        self.admin = make_admin()
        self.faculty = make_faculty()
        self.section = make_section()
        self.subject = make_subject(semester=self.section.semester)
        self.assignment = make_assignment(
            self.faculty, self.subject, self.section
        )
        self.student = make_student(
            section=self.section,
            semester=self.section.semester,
        )

        self.day = datetime.date.today()
        AttendanceConfig.objects.create(
            pk=1,
            correction_window_days=7,
            term_start_date=self.day,
            term_end_date=self.day,
        )

    def test_admin_can_access_master_data_and_reports(self):
        self.client.force_login(self.admin)

        self.assertEqual(
            self.client.get(reverse("masterdata:student_list")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("analytics:section_report")).status_code,
            200,
        )

    def test_faculty_can_mark_assigned_class_but_not_admin_pages(self):
        self.client.force_login(self.faculty.user)
        day = self.day
        mark_url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, day.isoformat()],
        )

        response = self.client.post(
            mark_url,
            {f"status_{self.student.pk}": Attendance.PRESENT},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Attendance.objects.filter(
                student=self.student,
                subject=self.subject,
                date=day,
                status=Attendance.PRESENT,
            ).exists()
        )
        self.assertEqual(
            self.client.get(reverse("masterdata:student_list")).status_code,
            403,
        )

    def test_student_can_open_personal_analytics_but_not_admin_pages(self):
        self.client.force_login(self.student.user)

        self.assertEqual(
            self.client.get(reverse("analytics:overall_attendance")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("masterdata:student_list")).status_code,
            403,
        )

    def test_unassigned_faculty_cannot_mark_another_facultys_class(self):
        other_faculty = make_faculty()
        self.client.force_login(other_faculty.user)

        mark_url = reverse(
            "attendance:mark",
            args=[self.assignment.pk, self.day.isoformat()],
        )

        response = self.client.post(
            mark_url,
            {f"status_{self.student.pk}": Attendance.PRESENT},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Attendance.objects.exists())
