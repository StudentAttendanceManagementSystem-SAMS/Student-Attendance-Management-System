import datetime

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView

from accounts.models import User
from accounts.permissions import (
    AdminRequiredMixin,
    faculty_owns_assignment,
    role_required,
)
from masterdata.models import FacultyAssignment, Student

from .forms import AttendanceConfigForm, ClassSelectForm
from .models import Attendance, AttendanceConfig


@role_required(User.FACULTY)
def select_class(request):
    faculty = getattr(request.user, "faculty_profile", None)
    assignments = FacultyAssignment.objects.none()

    if faculty is not None:
        assignments = (
            FacultyAssignment.objects.filter(faculty=faculty)
            .select_related("subject", "section")
            .order_by("subject__code", "section__name")
        )

    form = ClassSelectForm(
        request.GET or None,
        assignments=assignments,
    )

    if form.is_valid():
        assignment = form.cleaned_data["assignment"]
        selected_date = form.cleaned_data["date"]
        return redirect(
            "attendance:mark",
            assignment_id=assignment.pk,
            on_date=selected_date.isoformat(),
        )

    return render(
        request,
        "attendance/select_class.html",
        {
            "form": form,
            "has_assignments": assignments.exists(),
        },
    )


def _attendance_is_within_correction_window(day, config, today=None):
    """Return whether an attendance date is still editable.

    The configured window is inclusive: with a 7-day window, attendance
    dated today minus 7 days remains editable.
    """
    today = today or timezone.localdate()
    age_in_days = (today - day).days
    return 0 <= age_in_days <= config.correction_window_days


@role_required(User.FACULTY)
def mark_attendance(request, assignment_id, on_date):
    assignment = get_object_or_404(
        FacultyAssignment.objects.select_related(
            "subject",
            "section",
            "faculty",
        ),
        pk=assignment_id,
    )

    if not faculty_owns_assignment(request.user, assignment):
        raise PermissionDenied

    try:
        day = datetime.date.fromisoformat(on_date)
    except (TypeError, ValueError):
        raise Http404("Invalid attendance date")

    today = timezone.localdate()
    if day > today:
        raise Http404("Attendance cannot be marked for a future date.")

    students = list(
        Student.objects.filter(section=assignment.section).order_by("usn")
    )

    existing_records = Attendance.objects.filter(
        subject=assignment.subject,
        date=day,
        student__section=assignment.section,
    )
    has_existing_records = existing_records.exists()

    config = AttendanceConfig.get_solo()
    term_configured = bool(config.term_start_date and config.term_end_date)
    date_in_term = (
        term_configured
        and config.term_start_date <= day <= config.term_end_date
    )
    can_edit = (
        date_in_term
        and (
            not has_existing_records
            or _attendance_is_within_correction_window(day, config, today)
        )
    )

    if request.method == "POST":
        if not term_configured:
            raise PermissionDenied(
                "The administrator must configure the active academic term before attendance can be marked."
            )
        if not date_in_term:
            raise PermissionDenied(
                "Attendance can only be marked within the configured academic term."
            )
        if not can_edit:
            raise PermissionDenied(
                "The attendance correction window for this date has expired."
            )

        with transaction.atomic():
            created = updated = 0

            for student in students:
                status = request.POST.get(f"status_{student.pk}")
                if status not in (Attendance.PRESENT, Attendance.ABSENT):
                    status = Attendance.ABSENT

                _, was_created = Attendance.objects.update_or_create(
                    student=student,
                    subject=assignment.subject,
                    date=day,
                    defaults={
                        "faculty": assignment.faculty,
                        "status": status,
                    },
                )

                if was_created:
                    created += 1
                else:
                    updated += 1

        messages.success(
            request,
            f"Attendance saved: {created} new, {updated} updated.",
        )
        return redirect("attendance:select_class")

    existing = {
        record.student_id: record.status
        for record in existing_records
    }

    for student in students:
        student.current_status = existing.get(
            student.pk,
            Attendance.PRESENT,
        )

    context = {
        "assignment": assignment,
        "day": day,
        "students": students,
        "is_edit": has_existing_records,
        "can_edit": can_edit,
        "correction_window_days": config.correction_window_days,
        "term_configured": term_configured,
        "date_in_term": date_in_term,
        "term_start_date": config.term_start_date,
        "term_end_date": config.term_end_date,
    }
    return render(request, "attendance/mark.html", context)


class AttendanceConfigView(AdminRequiredMixin, FormView):
    form_class = AttendanceConfigForm
    template_name = "attendance/config.html"
    success_url = reverse_lazy("attendance:config")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = AttendanceConfig.get_solo()
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Attendance settings updated successfully.",
        )
        return super().form_valid(form)
