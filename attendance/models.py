
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Attendance(models.Model):
    PRESENT = "P"
    ABSENT = "A"
    STATUS_CHOICES = [
        (PRESENT, "Present"),
        (ABSENT, "Absent"),
    ]

    student = models.ForeignKey(
        "masterdata.Student",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    subject = models.ForeignKey(
        "masterdata.Subject",
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )
    faculty = models.ForeignKey(
        "masterdata.Faculty",
        on_delete=models.PROTECT,
        related_name="marked_attendance",
    )
    date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    marked_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject", "date"],
                name="unique_attendance_per_day",
            )
        ]
        ordering = ["-date", "student__usn"]

    def __str__(self):
        return (
            f"{self.student.usn} "
            f"{self.subject.code} {self.date} {self.status}"
        )


class AttendanceConfig(models.Model):
    threshold_percentage = models.PositiveSmallIntegerField(
        default=75,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    correction_window_days = models.PositiveSmallIntegerField(
        default=7,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(365),
        ],
        help_text=(
            "Number of days after an attendance date during which "
            "faculty may edit already-saved attendance."
        ),
    )
    term_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="First date of the institution's active academic term.",
    )
    term_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Last date of the institution's active academic term.",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    threshold_percentage__gte=0,
                    threshold_percentage__lte=100,
                ),
                name="attendance_threshold_0_100",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    correction_window_days__gte=0,
                    correction_window_days__lte=365,
                ),
                name="attendance_correction_window_0_365",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(term_start_date__isnull=True, term_end_date__isnull=True)
                    | models.Q(term_start_date__lte=models.F("term_end_date"))
                ),
                name="attendance_term_start_before_end",
            ),
        ]

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    threshold_percentage__gte=0,
                    threshold_percentage__lte=100,
                ),
                name="attendance_threshold_0_100",
            ),
        ]

    def __str__(self):
        return f"Minimum attendance: {self.threshold_percentage}%"

    @classmethod
    def get_solo(cls):
        """Return the single configuration, creating the default if needed."""
        config, _ = cls.objects.get_or_create(pk=1)
        return config
