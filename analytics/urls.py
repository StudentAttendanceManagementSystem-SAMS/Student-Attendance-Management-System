
from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path(
        "sections/",
        views.SectionWiseReportView.as_view(),
        name="section_report",
    ),
    path(
        "subjects/",
        views.SubjectWiseReportView.as_view(),
        name="subject_report",
    ),
    path(
        "below-threshold/",
        views.BelowThresholdStudentsView.as_view(),
        name="below_threshold",
    ),
]
