from django.views.generic import TemplateView

from accounts.permissions import AdminRequiredMixin

from .services import section_wise_report, subject_wise_report


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
