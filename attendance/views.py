import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from masterdata.models import FacultyAssignment, Student

from .forms import ClassSelectForm
from .models import Attendance


@login_required
def select_class(request):
    faculty = getattr(request.user, "faculty_profile", None)
    assignments = FacultyAssignment.objects.none()
    if faculty is not None:
        assignments = FacultyAssignment.objects.filter(faculty=faculty).select_related("subject", "section")
    form = ClassSelectForm(request.GET or None, assignments=assignments)
    if form.is_valid():
        assignment = form.cleaned_data["assignment"]
        on_date = form.cleaned_data["date"]
        return redirect("attendance:mark", assignment_id=assignment.pk, on_date=on_date.isoformat())
    return render(request, "attendance/select_class.html", {"form": form, "has_assignments": assignments.exists()})


@login_required
def mark_attendance(request, assignment_id, on_date):
    faculty = getattr(request.user, "faculty_profile", None)

    if faculty is None:
        raise Http404

    assignment = get_object_or_404(
        FacultyAssignment.objects.select_related(
            "subject", "section", "faculty"
        ),
        pk=assignment_id,
        faculty=faculty,
    )

    try:
        day = datetime.date.fromisoformat(on_date)
    except ValueError:
        raise Http404("Invalid date")

    students = Student.objects.filter(
        section=assignment.section
    ).order_by("usn")

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"status_{student.pk}")

            if status not in (Attendance.PRESENT, Attendance.ABSENT):
                status = Attendance.ABSENT

            Attendance.objects.update_or_create(
                student=student,
                subject=assignment.subject,
                date=day,
                defaults={
                    "faculty": assignment.faculty,
                    "status": status,
                },
            )

        messages.success(
            request,
            f"Attendance saved for {len(students)} students.",
        )
        return redirect("attendance:select_class")

    context = {
        "assignment": assignment,
        "day": day,
        "students": students,
    }
    return render(request, "attendance/mark.html", context)