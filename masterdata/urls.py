from django.urls import path
from . import views

app_name = "masterdata"

urlpatterns = [
    path("students/", views.StudentListView.as_view(), name="student_list"),
    path("students/add/", views.StudentCreateView.as_view(), name="student_create"),
    path("students/<int:pk>/edit/", views.StudentUpdateView.as_view(), name="student_update"),
    path("students/<int:pk>/deactivate/", views.StudentDeactivateView.as_view(), name="student_deactivate"),
    path("sections/", views.SectionListView.as_view(), name="section_list"),
    path("sections/add/", views.SectionCreateView.as_view(), name="section_create"),
    path("sections/<int:pk>/edit/", views.SectionUpdateView.as_view(), name="section_update"),
    path("sections/<int:pk>/delete/", views.SectionDeleteView.as_view(), name="section_delete"),
    path("subjects/", views.SubjectListView.as_view(), name="subject_list"),
    path("subjects/add/", views.SubjectCreateView.as_view(), name="subject_create"),
    path("subjects/<int:pk>/edit/", views.SubjectUpdateView.as_view(), name="subject_update"),
    path("subjects/<int:pk>/delete/", views.SubjectDeleteView.as_view(), name="subject_delete"),
    path("assignments/", views.FacultyAssignmentListView.as_view(), name="assignment_list"),
    path("assignments/add/", views.FacultyAssignmentCreateView.as_view(), name="assignment_create"),
    path("faculty/", views.FacultyListView.as_view(), name="faculty_list"),
    path("faculty/add/", views.FacultyCreateView.as_view(), name="faculty_create"),
    path("faculty/<int:pk>/edit/", views.FacultyUpdateView.as_view(), name="faculty_update"),
    path("faculty/<int:pk>/deactivate/", views.FacultyDeactivateView.as_view(), name="faculty_deactivate"),
]
