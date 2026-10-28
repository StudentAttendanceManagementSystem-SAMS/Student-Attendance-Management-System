import datetime

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from accounts.permissions import faculty_owns_assignment, role_required
from masterdata.models import FacultyAssignment, Student

from .forms import ClassSelectForm
from .models import Attendance


@role_required(User.FACULTY)
def select_class(request):
    faculty = getattr(request.user, "faculty_profile", None)
    assignments = FacultyAssignment.objects.none()

    if faculty is not None:
        assignments = FacultyAssignment.objects.filter(
            faculty=faculty
        ).select_related("subject", "section")

    form = ClassSelectForm(
        request.GET or None,
        assignments=assignments,
    )

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

    # Ensure faculty can only mark attendance for their own assignment.
    if not faculty_owns_assignment(request.user, assignment):
        raise PermissionDenied

    try:
        day = datetime.date.fromisoformat(on_date)
    except ValueError:
        raise Http404("Invalid date")

    students = list(
        Student.objects.filter(
            section=assignment.section,
        ).order_by("usn")
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