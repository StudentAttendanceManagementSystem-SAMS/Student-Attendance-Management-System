from django.core.validators import MaxValueValidator
from django.db import models


class Attendance(models.Model):
    PRESENT = "P"
    ABSENT = "A"
    STATUS_CHOICES = [
        (PRESENT, "Present"),
        (ABSENT, "Absent"),
    ]

    student = models.ForeignKey(
        "masterdata.Student", on_delete=models.CASCADE, related_name="attendance_records"
    )
    subject = models.ForeignKey(
        "masterdata.Subject", on_delete=models.PROTECT, related_name="attendance_records"
    )
    faculty = models.ForeignKey(
        "masterdata.Faculty", on_delete=models.PROTECT, related_name="marked_attendance"
    )
    date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    marked_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject", "date"], name="unique_attendance_per_day"
            )
        ]
        ordering = ["-date", "student__usn"]

    def __str__(self):
        return f"{self.student.usn} {self.subject.code} {self.date} {self.status}"


class AttendanceConfig(models.Model):
    threshold_percentage = models.PositiveSmallIntegerField(
        default=75, validators=[MaxValueValidator(100)]
    )

    def __str__(self):
        return f"Minimum attendance: {self.threshold_percentage}%"
