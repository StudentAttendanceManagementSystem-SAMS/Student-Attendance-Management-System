
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView

from accounts.permissions import AdminRequiredMixin
from masterdata.models import FacultyAssignment, Student

from .forms import AttendanceConfigForm, ClassSelectForm
from .models import Attendance, AttendanceConfig


@login_required
def select_class(request):
    faculty = getattr(request.user, "faculty_profile", None)
    assignments = FacultyAssignment.objects.none()

    if faculty is not None:
        assignments = FacultyAssignment.objects.filter(
            faculty=faculty
        ).select_related("subject", "section")

    form = ClassSelectForm(request.GET or None, assignments=assignments)

    if form.is_valid():
        assignment = form.cleaned_data["assignment"]
        on_date = form.cleaned_data["date"]
        return redirect(
            "attendance:mark",
            assignment_id=assignment.pk,
            on_date=on_date.isoformat(),
        )

    return render(
        request,
        "attendance/select_class.html",
        {
            "form": form,
            "has_assignments": assignments.exists(),
        },
    )


@login_required
def mark_attendance(request, assignment_id, on_date):
    assignment = get_object_or_404(
        FacultyAssignment.objects.select_related(
            "subject", "section", "faculty"
        ),
        pk=assignment_id,
    )

    try:
        day = datetime.date.fromisoformat(on_date)
    except ValueError:
        raise Http404("Invalid date")

    students = list(
        Student.objects.filter(section=assignment.section).order_by("usn")
    )

    if request.method == "POST":
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
        for record in Attendance.objects.filter(
            subject=assignment.subject,
            date=day,
            student__in=students,
        )
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
        "is_edit": bool(existing),
    }

    return render(request, "attendance/mark.html", context)


class AttendanceConfigView(AdminRequiredMixin, FormView):
    template_name = "attendance/config.html"
    form_class = AttendanceConfigForm
    success_url = reverse_lazy("attendance:config")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = AttendanceConfig.get_solo()
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Minimum attendance threshold updated successfully.",
        )
        return super().form_valid(form)
