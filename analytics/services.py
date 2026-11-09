from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count, Q

from attendance.models import Attendance, AttendanceConfig
from masterdata.models import FacultyAssignment, Section, Student, Subject

TWO_PLACES = Decimal("0.01")


def percentage(present_count, total_count):
    if not total_count:
        return None
    value = Decimal(present_count) * Decimal("100") / Decimal(total_count)
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _attendance_queryset(date_from=None, date_to=None):
    """Return records scoped to the configured active term and optional range."""
    records = Attendance.objects.all()
    config = AttendanceConfig.get_solo()
    if config.term_start_date:
        records = records.filter(date__gte=config.term_start_date)
    if config.term_end_date:
        records = records.filter(date__lte=config.term_end_date)
    if date_from:
        records = records.filter(date__gte=date_from)
    if date_to:
        records = records.filter(date__lte=date_to)
    return records


def _counts(records):
    total = records.count()
    present = records.filter(status=Attendance.PRESENT).count()
    absent = records.filter(status=Attendance.ABSENT).count()
    return {
        "total_records": total,
        "total_count": total,
        "present_count": present,
        "absent_count": absent,
        "percentage": percentage(present, total),
    }


def section_wise_report(date_from=None, date_to=None):
    date_filter = Q()
    config = AttendanceConfig.get_solo()
    if config.term_start_date:
        date_filter &= Q(students__attendance_records__date__gte=config.term_start_date)
    if config.term_end_date:
        date_filter &= Q(students__attendance_records__date__lte=config.term_end_date)
    if date_from:
        date_filter &= Q(students__attendance_records__date__gte=date_from)
    if date_to:
        date_filter &= Q(students__attendance_records__date__lte=date_to)

    sections = Section.objects.annotate(
        student_count=Count("students", distinct=True),
        total_records=Count(
            "students__attendance_records", filter=date_filter, distinct=True
        ),
        present_count=Count(
            "students__attendance_records",
            filter=date_filter & Q(students__attendance_records__status=Attendance.PRESENT),
            distinct=True,
        ),
        absent_count=Count(
            "students__attendance_records",
            filter=date_filter & Q(students__attendance_records__status=Attendance.ABSENT),
            distinct=True,
        ),
    ).order_by("name")

    return [
        {
            "section": section,
            "student_count": section.student_count,
            "total_records": section.total_records,
            "total_count": section.total_records,
            "present_count": section.present_count,
            "absent_count": section.absent_count,
            "percentage": percentage(section.present_count, section.total_records),
        }
        for section in sections
    ]


def subject_wise_report(date_from=None, date_to=None):
    date_filter = Q()
    config = AttendanceConfig.get_solo()
    if config.term_start_date:
        date_filter &= Q(attendance_records__date__gte=config.term_start_date)
    if config.term_end_date:
        date_filter &= Q(attendance_records__date__lte=config.term_end_date)
    if date_from:
        date_filter &= Q(attendance_records__date__gte=date_from)
    if date_to:
        date_filter &= Q(attendance_records__date__lte=date_to)

    subjects = Subject.objects.annotate(
        sections_with_records=Count(
            "attendance_records__student__section", filter=date_filter, distinct=True
        ),
        students_with_records=Count(
            "attendance_records__student", filter=date_filter, distinct=True
        ),
        total_records=Count("attendance_records", filter=date_filter, distinct=True),
        present_count=Count(
            "attendance_records",
            filter=date_filter & Q(attendance_records__status=Attendance.PRESENT),
            distinct=True,
        ),
        absent_count=Count(
            "attendance_records",
            filter=date_filter & Q(attendance_records__status=Attendance.ABSENT),
            distinct=True,
        ),
    ).order_by("code")

    return [
        {
            "subject": subject,
            "sections_with_records": subject.sections_with_records,
            "students_with_records": subject.students_with_records,
            "total_records": subject.total_records,
            "total_count": subject.total_records,
            "present_count": subject.present_count,
            "absent_count": subject.absent_count,
            "percentage": percentage(subject.present_count, subject.total_records),
        }
        for subject in subjects
    ]


def _student_attendance_summary(student, records):
    present_count = records.filter(status=Attendance.PRESENT).count()
    total_count = records.count()
    subject_rows = []
    subject_ids = records.values_list("subject_id", flat=True).distinct()
    subjects = Subject.objects.filter(pk__in=subject_ids).order_by("code")
    for subject in subjects:
        subject_records = records.filter(subject=subject)
        counts = _counts(subject_records)
        subject_rows.append({
            "subject": subject,
            "present_count": counts["present_count"],
            "total_count": counts["total_count"],
            "percentage": counts["percentage"],
        })
    return {
        "semester": student.semester,
        "subjects": subject_rows,
        "present_count": present_count,
        "total_count": total_count,
        "percentage": percentage(present_count, total_count),
    }


def overall_attendance_for_student(student, date_from=None, date_to=None):
    """Weighted attendance summary for subjects in the student's current semester."""
    records = _attendance_queryset(date_from, date_to).filter(
        student=student,
        subject__semester=student.semester,
    ).select_related("subject")
    return _student_attendance_summary(student, records)


def overall_attendance_for_faculty(faculty, date_from=None, date_to=None):
    """Summaries limited to students and subject/section pairs assigned to faculty."""
    assignments = faculty.assignments.select_related("section", "subject")
    rows = []
    for assignment in assignments:
        students = Student.objects.filter(
            section=assignment.section,
            semester=assignment.subject.semester,
        ).select_related("section", "user").order_by("usn")
        for student in students:
            records = _attendance_queryset(date_from, date_to).filter(
                student=student,
                subject__semester=student.semester,
                subject=assignment.subject,
            ).select_related("subject")
            if not records.exists():
                continue
            report = _student_attendance_summary(student, records)
            rows.append({"student": student, "section": assignment.section, **report})
    # A student may have several assignments; combine the assigned-subject records.
    combined = {}
    for row in rows:
        key = row["student"].pk
        if key not in combined:
            combined[key] = {
                "student": row["student"], "section": row["section"],
                "semester": row["semester"], "subjects": [],
                "present_count": 0, "total_count": 0,
            }
        target = combined[key]
        target["subjects"].extend(row["subjects"])
        target["present_count"] += row["present_count"]
        target["total_count"] += row["total_count"]
    result = list(combined.values())
    for row in result:
        row["percentage"] = percentage(row["present_count"], row["total_count"])
    return sorted(result, key=lambda item: (item["section"].name, item["student"].usn))


def faculty_subject_report(faculty, section_id, subject_id, date_from=None, date_to=None):
    """Return a student-wise report only for an exact faculty assignment."""
    assignment = FacultyAssignment.objects.select_related("section", "subject").filter(
        faculty=faculty, section_id=section_id, subject_id=subject_id
    ).first()
    if assignment is None:
        return None

    rows = []
    for student in Student.objects.filter(
        section=assignment.section,
        semester=assignment.subject.semester,
    ).order_by("usn"):
        records = _attendance_queryset(date_from, date_to).filter(
            student=student, subject=assignment.subject
        )
        counts = _counts(records)
        rows.append({"student": student, **counts})
    return {"assignment": assignment, "rows": rows}


def student_attendance_history(student, subject_id=None, date_from=None, date_to=None):
    records = _attendance_queryset(date_from, date_to).filter(
        student=student,
        subject__semester=student.semester,
    ).select_related("subject", "faculty").order_by("-date", "subject__code")
    if subject_id:
        records = records.filter(subject_id=subject_id)
    return records


def below_threshold_students(faculty=None, date_from=None, date_to=None):
    """Return students below threshold overall and/or in any relevant subject.

    When faculty is supplied, only that faculty member's assigned subject-section
    combinations are considered. Each student appears once, with separate overall
    and subject-level results.
    """
    threshold = AttendanceConfig.get_solo().threshold_percentage
    students = Student.objects.select_related("section").order_by("section__name", "usn")
    results = []
    for student in students:
        records = _attendance_queryset(date_from, date_to).filter(
            student=student,
            subject__semester=student.semester,
        )
        if faculty is not None:
            assigned_subject_ids = faculty.assignments.filter(
                section=student.section,
                subject__semester=student.semester,
            ).values_list("subject_id", flat=True)
            records = records.filter(subject_id__in=assigned_subject_ids)
            if not assigned_subject_ids.exists():
                continue

        overall = _counts(records)
        subject_results = []
        for subject in Subject.objects.filter(
            attendance_records__student=student,
            semester=student.semester,
        ).distinct().order_by("code"):
            subject_records = records.filter(subject=subject)
            counts = _counts(subject_records)
            if counts["percentage"] is not None and counts["percentage"] < threshold:
                subject_results.append({"subject": subject, **counts})

        overall_below = (
            overall["percentage"] is not None and overall["percentage"] < threshold
        )
        if overall_below or subject_results:
            results.append({
                "student": student,
                "section": student.section,
                "present_count": overall["present_count"],
                "total_count": overall["total_count"],
                "percentage": overall["percentage"],
                "threshold": threshold,
                "overall_below": overall_below,
                "subject_results": subject_results,
            })
    return results
