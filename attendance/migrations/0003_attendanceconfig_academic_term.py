# Add institution-wide active academic-term boundaries.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0002_attendanceconfig_correction_window"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendanceconfig",
            name="term_start_date",
            field=models.DateField(
                blank=True,
                help_text="First date of the institution's active academic term.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="attendanceconfig",
            name="term_end_date",
            field=models.DateField(
                blank=True,
                help_text="Last date of the institution's active academic term.",
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="attendanceconfig",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(term_start_date__isnull=True, term_end_date__isnull=True)
                    | models.Q(term_start_date__lte=models.F("term_end_date"))
                ),
                name="attendance_term_start_before_end",
            ),
        ),
    ]
