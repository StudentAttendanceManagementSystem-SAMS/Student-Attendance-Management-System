from django.urls import path
from .history_views import attendance_history
from . import views

app_name = "attendance"

urlpatterns = [
    path("select/", views.select_class, name="select_class"),

    path(
        "mark/<int:assignment_id>/<str:on_date>/",
        views.mark_attendance,
        name="mark",
    ),

    path(
        "history/<int:student_id>/<int:subject_id>/",
        attendance_history,
        name="history",
    ),

    path(
        "settings/threshold/",
        views.AttendanceConfigView.as_view(),
        name="config",
    ),
]