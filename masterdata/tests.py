from django.db import IntegrityError, transaction
from django.test import TestCase

from .factories import make_faculty, make_section, make_student, make_subject
from .models import FacultyAssignment, SubjectSection


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
