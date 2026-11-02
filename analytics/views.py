from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView

from accounts.models import User
from accounts.permissions import AdminRequiredMixin

from .services import (
    below_threshold_students,
    overall_attendance_for_faculty,
    overall_attendance_for_student,
    section_wise_report,
    subject_wise_report,
)


class SectionWiseReportView(AdminRequiredMixin, TemplateView):
    template_name = "analytics/section_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report"] = section_wise_report()
        return context


class SubjectWiseReportView(AdminRequiredMixin, TemplateView):
    template_name = "analytics/subject_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report"] = subject_wise_report()
        return context


class BelowThresholdStudentsView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/below_threshold.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role not in (User.ADMIN, User.FACULTY):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = below_threshold_students()
        if self.request.user.role == User.ADMIN:
            context["students"] = students
        else:
            faculty = self.request.user.faculty_profile
            assigned_section_ids = set(
                faculty.assignments.values_list("section_id", flat=True)
            )
            context["students"] = [
                item for item in students if item["section"].id in assigned_section_ids
            ]
        context["threshold"] = students[0]["threshold"] if students else None
        return context


class OverallAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/overall_attendance.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role not in (User.STUDENT, User.FACULTY):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == User.STUDENT:
            context["student_report"] = overall_attendance_for_student(
                self.request.user.student_profile
            )
        else:
            context["faculty_reports"] = overall_attendance_for_faculty(
                self.request.user.faculty_profile
            )
        return context
