from django.urls import path

from . import views

app_name = "masterdata"

urlpatterns = [
    path("students/", views.StudentListView.as_view(), name="student_list"),
    path("students/add/", views.StudentCreateView.as_view(), name="student_create"),
    path("students/<int:pk>/edit/", views.StudentUpdateView.as_view(), name="student_update"),
    path("sections/", views.SectionListView.as_view(), name="section_list"),
    path("sections/add/", views.SectionCreateView.as_view(), name="section_create"),
    path("subjects/", views.SubjectListView.as_view(), name="subject_list"),
    path("subjects/add/", views.SubjectCreateView.as_view(), name="subject_create"),
]
