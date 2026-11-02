from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Count, Q

from attendance.models import Attendance, AttendanceConfig
from masterdata.models import Section, Student, Subject


TWO_PLACES = Decimal("0.01")


def percentage(present_count, total_count):
    if total_count == 0:
        return None

    value = Decimal(present_count) * 100 / Decimal(total_count)
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def section_wise_report():
    sections = Section.objects.annotate(
        student_count=Count("students", distinct=True),
        total_records=Count("students__attendance_records", distinct=True),
        present_count=Count(
            "students__attendance_records",
            filter=Q(students__attendance_records__status=Attendance.PRESENT),
            distinct=True,
        ),
        absent_count=Count(
            "students__attendance_records",
            filter=Q(students__attendance_records__status=Attendance.ABSENT),
            distinct=True,
        ),
    ).order_by("name")

    return [
        {
            "section": section,
            "student_count": section.student_count,
            "total_records": section.total_records,
            "present_count": section.present_count,
            "absent_count": section.absent_count,
            "percentage": percentage(section.present_count, section.total_records),
        }
        for section in sections
    ]


def subject_wise_report():
    subjects = Subject.objects.annotate(
        sections_with_records=Count("attendance_records__student__section", distinct=True),
        students_with_records=Count("attendance_records__student", distinct=True),
        total_records=Count("attendance_records", distinct=True),
        present_count=Count(
            "attendance_records",
            filter=Q(attendance_records__status=Attendance.PRESENT),
            distinct=True,
        ),
        absent_count=Count(
            "attendance_records",
            filter=Q(attendance_records__status=Attendance.ABSENT),
            distinct=True,
        ),
    ).order_by("code")

    return [
        {
            "subject": subject,
            "sections_with_records": subject.sections_with_records,
            "students_with_records": subject.students_with_records,
            "total_records": subject.total_records,
            "present_count": subject.present_count,
            "absent_count": subject.absent_count,
            "percentage": percentage(subject.present_count, subject.total_records),
        }
        for subject in subjects
    ]


def below_threshold_students():
    threshold = AttendanceConfig.get_solo().threshold_percentage
    students = Student.objects.select_related("section").order_by("section__name", "usn")
    results = []

    for student in students:
        records = Attendance.objects.filter(student=student)
        total_count = records.count()
        present_count = records.filter(status=Attendance.PRESENT).count()
        attendance_percentage = percentage(present_count, total_count)

        if attendance_percentage is not None and attendance_percentage < threshold:
            results.append(
                {
                    "student": student,
                    "section": student.section,
                    "present_count": present_count,
                    "total_count": total_count,
                    "percentage": attendance_percentage,
                    "threshold": threshold,
                }
            )
    return results


def overall_attendance_for_student(student):
    """Return the weighted overall and subject-wise attendance for a student's current semester.

    A record counts only when its subject belongs to the student's current semester.
    The overall percentage is total presents / total recorded classes, not an
    unweighted average of subject percentages. This makes the result match the
    aggregate of subject-wise attendance counts.
    """
    records = Attendance.objects.filter(
        student=student,
        subject__semester=student.semester,
    ).select_related("subject")

    subject_rows = []
    total_count = 0
    present_count = 0

    subject_ids = records.values_list("subject_id", flat=True).distinct()
    subjects = Subject.objects.filter(pk__in=subject_ids).order_by("code")
    for subject in subjects:
        subject_records = records.filter(subject=subject)
        subject_total = subject_records.count()
        subject_present = subject_records.filter(status=Attendance.PRESENT).count()
        total_count += subject_total
        present_count += subject_present
        subject_rows.append(
            {
                "subject": subject,
                "present_count": subject_present,
                "total_count": subject_total,
                "percentage": percentage(subject_present, subject_total),
            }
        )

    return {
        "semester": student.semester,
        "subjects": subject_rows,
        "present_count": present_count,
        "total_count": total_count,
        "percentage": percentage(present_count, total_count),
    }


def overall_attendance_for_faculty(faculty):
    """Return per-student overall attendance for the faculty member's assigned sections."""
    assignments = faculty.assignments.select_related("section", "subject")
    section_ids = assignments.values_list("section_id", flat=True).distinct()
    students = Student.objects.filter(section_id__in=section_ids).select_related(
        "section", "user"
    ).order_by("section__name", "usn")

    results = []
    for student in students:
        report = overall_attendance_for_student(student)
        # Keep only students with records in their current semester.
        if report["total_count"]:
            results.append({"student": student, **report})
    return results
