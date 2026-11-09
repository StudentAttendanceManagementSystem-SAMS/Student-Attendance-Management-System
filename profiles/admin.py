from django.contrib import admin
from .models import StudentProfile, FacultyProfile, AdminProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("student", "joining_year", "current_cgpa", "current_sgpa")
    search_fields = ("student__usn", "student__name")

@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ("faculty", "designation", "date_of_joining")
    search_fields = ("faculty__employee_id", "faculty__name")

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "designation", "date_of_joining")
