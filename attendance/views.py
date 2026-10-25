from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from masterdata.models import FacultyAssignment


class SelectClassView(LoginRequiredMixin, ListView):
    template_name = "attendance/select_class.html"
    context_object_name = "assignments"

    def get_queryset(self):
        if hasattr(self.request.user, "faculty_profile"):
            return self.request.user.faculty_profile.assignments.select_related("subject", "section")
        return FacultyAssignment.objects.none()
