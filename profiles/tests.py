from datetime import date
from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from masterdata.models import Section, Student, Faculty
from .models import StudentProfile, FacultyProfile, AdminProfile


class ProfileAccessTests(TestCase):
    def setUp(self):
        section = Section.objects.create(name="PROFILE-S1-A", semester=1, academic_year="2026-27")
        self.student_user = User.objects.create_user(username="profile-student", password="TestPass123!", role=User.STUDENT)
        self.student = Student.objects.create(user=self.student_user, usn="PROFILE001", name="Test Student", section=section, semester=1)
        self.faculty_user = User.objects.create_user(username="profile-faculty", password="TestPass123!", role=User.FACULTY)
        Faculty.objects.create(user=self.faculty_user, employee_id="PROFILE-F001", name="Test Faculty", department="CSE")
        self.admin_user = User.objects.create_user(username="profile-admin", password="TestPass123!", role=User.ADMIN, is_staff=True)

    def test_student_sees_own_profile_and_academic_data(self):
        StudentProfile.objects.create(student=self.student, current_cgpa="8.50", current_sgpa="9.00")
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("profiles:my_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "8.50")
        self.assertContains(response, "Parent / guardian information")

    def test_faculty_profile_shows_teaching_profile(self):
        self.client.force_login(self.faculty_user)
        response = self.client.get(reverse("profiles:my_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FACULTY PROFILE")

    def test_admin_profile_is_created_on_first_visit(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("profiles:my_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(AdminProfile.objects.filter(user=self.admin_user).exists())

    def test_student_cannot_open_another_users_profile_by_id(self):
        self.client.force_login(self.student_user)
        response = self.client.get("/profile/999/")
        self.assertEqual(response.status_code, 404)
