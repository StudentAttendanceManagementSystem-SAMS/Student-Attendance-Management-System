from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .factories import make_admin, make_faculty, make_section, make_student, make_subject
from .models import FacultyAssignment, Section, Student, Subject, SubjectSection


class MasterDataModelTests(TestCase):
    def test_usn_must_be_unique(self):
        student = make_student()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                make_student(usn=student.usn)

    def test_employee_id_must_be_unique(self):
        faculty = make_faculty()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                make_faculty(employee_id=faculty.employee_id)

    def test_section_name_must_be_unique(self):
        section = make_section()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                make_section(name=section.name)

    def test_subject_can_be_mapped_to_a_section_only_once(self):
        subject, section = make_subject(), make_section()
        SubjectSection.objects.create(subject=subject, section=section)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SubjectSection.objects.create(subject=subject, section=section)

    def test_faculty_assignment_must_be_unique(self):
        faculty, subject, section = make_faculty(), make_subject(), make_section()
        FacultyAssignment.objects.create(faculty=faculty, subject=subject, section=section)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                FacultyAssignment.objects.create(faculty=faculty, subject=subject, section=section)


class StudentPageTests(TestCase):
    def setUp(self):
        self.client.force_login(make_admin())
        self.section = make_section()

    def student_data(self, **overrides):
        data = {
            "usn": "PES2UG24CS901",
            "name": "Test Student",
            "section": self.section.pk,
            "semester": 3,
            "contact_no": "9876543210",
            "password": "pass12345",
        }
        data.update(overrides)
        return data

    def test_create_student_also_creates_login_account(self):
        response = self.client.post(reverse("masterdata:student_create"), self.student_data())
        self.assertRedirects(response, reverse("masterdata:student_list"))
        student = Student.objects.get(usn="PES2UG24CS901")
        self.assertEqual(student.user.role, User.STUDENT)
        self.assertTrue(student.user.check_password("pass12345"))

    def test_student_list_shows_students(self):
        make_student(name="Listed Student")
        response = self.client.get(reverse("masterdata:student_list"))
        self.assertContains(response, "Listed Student")

    def test_update_changes_the_section(self):
        student = make_student()
        new_section = make_section()
        response = self.client.post(
            reverse("masterdata:student_update", args=[student.pk]),
            {"name": student.name, "section": new_section.pk, "semester": 3, "contact_no": "9000000000"},
        )
        self.assertRedirects(response, reverse("masterdata:student_list"))
        student.refresh_from_db()
        self.assertEqual(student.section, new_section)


    def test_duplicate_usn_is_rejected_with_a_clear_message(self):
        make_student(usn="PES2UG24CS901")
        response = self.client.post(reverse("masterdata:student_create"), self.student_data())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A student with this USN already exists.")
        self.assertEqual(Student.objects.filter(usn="PES2UG24CS901").count(), 1)

    def test_usn_is_stored_in_upper_case(self):
        self.client.post(reverse("masterdata:student_create"), self.student_data(usn="pes2ug24cs902"))
        self.assertTrue(Student.objects.filter(usn="PES2UG24CS902").exists())


class SectionPageTests(TestCase):
    def setUp(self):
        self.client.force_login(make_admin())

    def test_section_list_shows_sections(self):
        make_section(name="CSE-9Z")
        response = self.client.get(reverse("masterdata:section_list"))
        self.assertContains(response, "CSE-9Z")

    def test_create_section_saves_and_lists_it(self):
        data = {"name": "CSE-7B", "semester": 5, "academic_year": "2026-27"}
        response = self.client.post(reverse("masterdata:section_create"), data)
        self.assertRedirects(response, reverse("masterdata:section_list"))
        self.assertTrue(Section.objects.filter(name="CSE-7B").exists())

    def test_section_appears_in_the_student_form_dropdown(self):
        make_section(name="CSE-8C")
        response = self.client.get(reverse("masterdata:student_create"))
        self.assertContains(response, "CSE-8C")


class SubjectPageTests(TestCase):
    def setUp(self):
        self.client.force_login(make_admin())

    def test_subject_list_shows_subjects(self):
        make_subject(code="UE24XX999")
        response = self.client.get(reverse("masterdata:subject_list"))
        self.assertContains(response, "UE24XX999")

    def test_create_subject(self):
        data = {"code": "UE24CS777", "name": "Test Subject", "semester": 4}
        response = self.client.post(reverse("masterdata:subject_create"), data)
        self.assertRedirects(response, reverse("masterdata:subject_list"))
        self.assertTrue(Subject.objects.filter(code="UE24CS777").exists())

    def test_duplicate_subject_code_is_rejected(self):
        make_subject(code="UE24CS777")
        data = {"code": "UE24CS777", "name": "Another", "semester": 4}
        response = self.client.post(reverse("masterdata:subject_create"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Subject.objects.filter(code="UE24CS777").count(), 1)
