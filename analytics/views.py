
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView

from accounts.models import User
from accounts.permissions import AdminRequiredMixin

from .services import (
    below_threshold_students,
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
        # LoginRequiredMixin redirects unauthenticated users to login.
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        # Only administrators and faculty can access this page.
        if request.user.role not in (User.ADMIN, User.FACULTY):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        students = below_threshold_students()

        if self.request.user.role == User.ADMIN:
            # Administrators can see all students below the threshold.
            context["students"] = students
        else:
            # Faculty can see students in their assigned sections.
            faculty = self.request.user.faculty_profile
            assigned_section_ids = set(
                faculty.assignments.values_list("section_id", flat=True)
            )

            context["students"] = [
                item
                for item in students
                if item["section"].id in assigned_section_ids
            ]

        context["threshold"] = (
            students[0]["threshold"] if students else None
        )

        return context
