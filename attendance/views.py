import datetime

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from masterdata.models import FacultyAssignment, Student

from .forms import ClassSelectForm


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
    assignment = get_object_or_404(
        FacultyAssignment.objects.select_related("subject", "section", "faculty"),
        pk=assignment_id,
    )
    try:
        day = datetime.date.fromisoformat(on_date)
    except ValueError:
        raise Http404("Invalid date")
    students = Student.objects.filter(section=assignment.section).order_by("usn")
    context = {"assignment": assignment, "day": day, "students": students}
    return render(request, "attendance/mark.html", context)

