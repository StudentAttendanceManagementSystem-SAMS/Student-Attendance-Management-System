from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone

from accounts.models import User
from analytics.services import (
    below_threshold_students,
    overall_attendance_for_student,
)
from attendance.models import Attendance, AttendanceConfig
from masterdata.models import FacultyAssignment, Faculty, Section, Student, Subject


@login_required
def home(request):
    """Render a dashboard scoped to the authenticated user's application role."""
    user = request.user

    if user.role == User.ADMIN:
        context = {
            "student_count": Student.objects.count(),
            "faculty_count": Faculty.objects.count(),
            "section_count": Section.objects.count(),
            "subject_count": Subject.objects.count(),
            "low_attendance_count": len(below_threshold_students()),
            "threshold": AttendanceConfig.get_solo().threshold_percentage,
        }
        return render(request, "dashboard/admin.html", context)

    if user.role == User.FACULTY:
        faculty = getattr(user, "faculty_profile", None)
        if faculty is None:
            raise PermissionDenied("No faculty profile is linked to this account.")

        today = timezone.localdate()
        assignments = FacultyAssignment.objects.filter(
            faculty=faculty
        ).select_related("subject", "section").order_by(
            "subject__code", "section__name"
        )
        assignment_rows = []
        for assignment in assignments:
            records = Attendance.objects.filter(
                faculty=faculty,
                subject=assignment.subject,
                student__section=assignment.section,
                date=today,
            )
            assignment_rows.append({
                "assignment": assignment,
                "marked_today": records.exists(),
                "record_count": records.count(),
                "student_count": Student.objects.filter(
                    section=assignment.section,
                    semester=assignment.subject.semester,
                ).count(),
            })

        context = {
            "assignments": assignment_rows,
            "today": today,
            "marked_count": sum(row["marked_today"] for row in assignment_rows),
            "assignment_count": len(assignment_rows),
        }
        return render(request, "dashboard/faculty.html", context)

    if user.role == User.STUDENT:
        student = getattr(user, "student_profile", None)
        if student is None:
            raise PermissionDenied("No student profile is linked to this account.")

        report = overall_attendance_for_student(student)
        threshold = AttendanceConfig.get_solo().threshold_percentage
        below_subjects = [
            row for row in report["subjects"]
            if row["percentage"] is not None and row["percentage"] < threshold
        ]
        context = {
            "student": student,
            "report": report,
            "threshold": threshold,
            "below_subjects": below_subjects,
        }
        return render(request, "dashboard/student.html", context)

    raise PermissionDenied("This account does not have a supported SAMS role.")
