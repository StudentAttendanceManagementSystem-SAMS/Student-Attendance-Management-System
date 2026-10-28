
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
        total_records=Count(
            "students__attendance_records", distinct=True
        ),
        present_count=Count(
            "students__attendance_records",
            filter=Q(
                students__attendance_records__status=Attendance.PRESENT
            ),
            distinct=True,
        ),
        absent_count=Count(
            "students__attendance_records",
            filter=Q(
                students__attendance_records__status=Attendance.ABSENT
            ),
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
            "percentage": percentage(
                section.present_count, section.total_records
            ),
        }
        for section in sections
    ]


def subject_wise_report():
    subjects = Subject.objects.annotate(
        sections_with_records=Count(
            "attendance_records__student__section", distinct=True
        ),
        students_with_records=Count(
            "attendance_records__student", distinct=True
        ),
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
            "percentage": percentage(
                subject.present_count, subject.total_records
            ),
        }
        for subject in subjects
    ]


def below_threshold_students():
    threshold = AttendanceConfig.get_solo().threshold_percentage

    students = Student.objects.select_related(
        "section"
    ).order_by("section__name", "usn")

    results = []

    for student in students:
        records = Attendance.objects.filter(student=student)

        total_count = records.count()
        present_count = records.filter(
            status=Attendance.PRESENT
        ).count()

        attendance_percentage = percentage(
            present_count, total_count
        )

        if (
            attendance_percentage is not None
            and attendance_percentage < threshold
        ):
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
