import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from masterdata.models import FacultyAssignment, Student

from .forms import ClassSelectForm
from .models import Attendance, AttendanceConfig


@login_required
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


def attendance_edit_deadline(day, config):
    return day + datetime.timedelta(
        days=config.correction_window_days
    )


def can_edit_attendance(day, config, today=None):
    """Return whether an existing attendance record is still editable."""
    today = today or datetime.date.today()

    if day > today:
        return False

    return today <= attendance_edit_deadline(day, config)


@login_required
def mark_attendance(request, assignment_id, on_date):
    assignment = get_object_or_404(
        FacultyAssignment.objects.select_related(
            "subject",
            "section",
            "faculty",
        ),
        pk=assignment_id,
    )

    # A faculty member may only view or mark attendance for their own assignment.
    faculty = getattr(request.user, "faculty_profile", None)
    if faculty is None or assignment.faculty_id != faculty.pk:
        raise PermissionDenied

    try:
        day = datetime.date.fromisoformat(on_date)
    except ValueError:
        raise Http404("Invalid date")

    config = AttendanceConfig.get_solo()

    # Attendance cannot be marked until the administrator configures the term.
    if not config.term_start_date or not config.term_end_date:
        raise PermissionDenied(
            "The administrator has not configured the active term."
        )

    if not config.term_start_date <= day <= config.term_end_date:
        raise PermissionDenied(
            "Attendance date is outside the active academic term."
        )

    today = datetime.date.today()
    if day > today:
        raise PermissionDenied(
            "Attendance cannot be marked for a future date."
        )

    students = list(
        Student.objects.filter(section=assignment.section).order_by("usn")
    )

    existing_records = Attendance.objects.filter(
        subject=assignment.subject,
        date=day,
        student__section=assignment.section,
    )
    has_existing = existing_records.exists()

    # The correction window applies only when records already exist.
    if has_existing and not can_edit_attendance(day, config, today):
        raise PermissionDenied(
            "The authorised attendance correction window has expired."
        )

    if request.method == "POST":
        created = 0
        updated = 0

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
        "is_edit": bool(existing),
    }
    return render(request, "attendance/mark.html", context)
