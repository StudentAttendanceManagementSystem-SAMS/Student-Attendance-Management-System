# Generated for the attendance configuration and correction-window support.
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0001_attendance_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attendanceconfig",
            name="threshold_percentage",
            field=models.PositiveSmallIntegerField(
                default=75,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ],
            ),
        ),
        migrations.AddField(
            model_name="attendanceconfig",
            name="correction_window_days",
            field=models.PositiveSmallIntegerField(
                default=7,
                help_text=(
                    "Number of days after an attendance date during which "
                    "faculty may edit already-saved attendance."
                ),
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(365),
                ],
            ),
        ),
        migrations.AddConstraint(
            model_name="attendanceconfig",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("threshold_percentage__gte", 0),
                    ("threshold_percentage__lte", 100),
                ),
                name="attendance_threshold_0_100",
            ),
        ),
        migrations.AddConstraint(
            model_name="attendanceconfig",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("correction_window_days__gte", 0),
                    ("correction_window_days__lte", 365),
                ),
                name="attendance_correction_window_0_365",
            ),
        ),
    ]
