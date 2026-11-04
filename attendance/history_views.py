from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from accounts.models import User
from accounts.permissions import role_required
from masterdata.models import Student, Subject
from .models import Attendance


@role_required(User.ADMIN, User.FACULTY, User.STUDENT)
def attendance_history(request, student_id, subject_id):
    student = get_object_or_404(
        Student.objects.select_related("section", "user"),
        pk=student_id,
    )
    subject = get_object_or_404(Subject, pk=subject_id)

    if request.user.role == User.STUDENT:
        if not hasattr(request.user, "student_profile"):
            raise PermissionDenied
        if request.user.student_profile.pk != student.pk:
            raise PermissionDenied

    elif request.user.role == User.FACULTY:
        faculty = getattr(request.user, "faculty_profile", None)
        if faculty is None or not faculty.assignments.filter(
            subject=subject,
            section=student.section,
        ).exists():
            raise PermissionDenied

    records = Attendance.objects.filter(
        student=student,
        subject=subject,
    ).select_related("faculty").order_by("-date")

    return render(
        request,
        "attendance/history.html",
        {"student": student, "subject": subject, "records": records},
    )
