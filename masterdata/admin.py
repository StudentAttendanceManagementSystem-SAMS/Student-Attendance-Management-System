from django.contrib import admin

from .models import Faculty, FacultyAssignment, Section, Student, Subject, SubjectSection

admin.site.register(Section)
admin.site.register(Subject)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(SubjectSection)
admin.site.register(FacultyAssignment)
