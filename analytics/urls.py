from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("sections/", views.SectionWiseReportView.as_view(), name="section_report"),
    path("subjects/", views.SubjectWiseReportView.as_view(), name="subject_report"),
    path("below-threshold/", views.BelowThresholdStudentsView.as_view(), name="below_threshold"),
    path("overall/", views.OverallAttendanceView.as_view(), name="overall_attendance"),
    path("faculty/subject-report/", views.FacultySubjectReportView.as_view(), name="faculty_subject_report"),
    path("student-history/", views.StudentAttendanceHistoryView.as_view(), name="my_attendance_history"),
    path("students/<int:student_id>/history/", views.StudentAttendanceHistoryView.as_view(), name="student_attendance_history"),
]
