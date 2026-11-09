from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from accounts.models import User
from attendance.models import AttendanceConfig
from accounts.permissions import AdminRequiredMixin
from masterdata.models import Student

from .forms import (
    DateRangeFilterForm,
    FacultySubjectReportForm,
    StudentHistoryFilterForm,
)
from .services import (
    below_threshold_students,
    faculty_subject_report,
    overall_attendance_for_faculty,
    overall_attendance_for_student,
    section_wise_report,
    student_attendance_history,
    subject_wise_report,
)


class DateFilteredAdminReportView(AdminRequiredMixin, TemplateView):
    form_class = DateRangeFilterForm

    def get_filter_form(self):
        return self.form_class(self.request.GET)

    def get_date_filters(self):
        form = self.get_filter_form()
        if form.is_valid():
            return form.cleaned_data.get("date_from"), form.cleaned_data.get("date_to"), form
        return None, None, form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_from, date_to, form = self.get_date_filters()
        context.update({"filter_form": form, "date_from": date_from, "date_to": date_to})
        return context


class SectionWiseReportView(DateFilteredAdminReportView):
    template_name = "analytics/section_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report"] = (
            section_wise_report(context["date_from"], context["date_to"])
            if context["filter_form"].is_valid() else []
        )
        return context


class SubjectWiseReportView(DateFilteredAdminReportView):
    template_name = "analytics/subject_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report"] = (
            subject_wise_report(context["date_from"], context["date_to"])
            if context["filter_form"].is_valid() else []
        )
        return context


class BelowThresholdStudentsView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/below_threshold.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role not in (User.ADMIN, User.FACULTY):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DateRangeFilterForm(self.request.GET)
        date_from = date_to = None
        if form.is_valid():
            date_from = form.cleaned_data.get("date_from")
            date_to = form.cleaned_data.get("date_to")
        faculty = None
        if self.request.user.role == User.FACULTY:
            faculty = getattr(self.request.user, "faculty_profile", None)
            if faculty is None:
                raise PermissionDenied
        students = (
            below_threshold_students(faculty, date_from, date_to)
            if form.is_valid() else []
        )
        context.update({
            "students": students,
            "threshold": students[0]["threshold"] if students else None,
            "filter_form": form,
            "date_from": date_from,
            "date_to": date_to,
        })
        return context


class OverallAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/overall_attendance.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role not in (User.STUDENT, User.FACULTY):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DateRangeFilterForm(self.request.GET)
        date_from = date_to = None
        if form.is_valid():
            date_from = form.cleaned_data.get("date_from")
            date_to = form.cleaned_data.get("date_to")
        if self.request.user.role == User.STUDENT:
            student = getattr(self.request.user, "student_profile", None)
            if student is None:
                raise PermissionDenied
            context["student_report"] = (
                overall_attendance_for_student(student, date_from, date_to)
                if form.is_valid() else None
            )
        else:
            faculty = getattr(self.request.user, "faculty_profile", None)
            if faculty is None:
                raise PermissionDenied
            context["faculty_reports"] = (
                overall_attendance_for_faculty(faculty, date_from, date_to)
                if form.is_valid() else []
            )
        context["filter_form"] = form
        context["threshold"] = AttendanceConfig.get_solo().threshold_percentage
        context["date_from"] = date_from
        context["date_to"] = date_to
        return context


class FacultySubjectReportView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/faculty_subject_report.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role != User.FACULTY:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = getattr(self.request.user, "faculty_profile", None)
        if faculty is None:
            raise PermissionDenied
        form = FacultySubjectReportForm(self.request.GET, faculty=faculty)
        report = None
        if self.request.GET and form.is_valid():
            data = form.cleaned_data
            report = faculty_subject_report(
                faculty,
                data["section"].pk,
                data["subject"].pk,
                data.get("date_from"),
                data.get("date_to"),
            )
        context.update({"form": form, "report": report})
        return context


class StudentAttendanceHistoryView(LoginRequiredMixin, TemplateView):
    template_name = "analytics/student_history.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role not in (
            User.ADMIN, User.FACULTY, User.STUDENT
        ):
            raise PermissionDenied
        if request.user.is_authenticated:
            has_student_id = "student_id" in kwargs
            if request.user.role == User.STUDENT and has_student_id:
                raise PermissionDenied
            if request.user.role in (User.ADMIN, User.FACULTY) and not has_student_id:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = None
        if self.request.user.role == User.STUDENT:
            student = get_object_or_404(Student, user=self.request.user)
        else:
            student = get_object_or_404(Student, pk=self.kwargs["student_id"])
            if self.request.user.role == User.FACULTY:
                faculty = getattr(self.request.user, "faculty_profile", None)
                if faculty is None:
                    raise PermissionDenied
        form = StudentHistoryFilterForm(
            self.request.GET,
            student=student,
            faculty=faculty,
        )
        date_from = date_to = subject_id = None
        if form.is_valid():
            date_from = form.cleaned_data.get("date_from")
            date_to = form.cleaned_data.get("date_to")
            selected_subject = form.cleaned_data.get("subject")
            subject_id = selected_subject.pk if selected_subject else None
        context.update({
            "student": student,
            "records": (
                student_attendance_history(student, subject_id, date_from, date_to)
                if form.is_valid() else []
            ),
            "filter_form": form,
        })
        return context
