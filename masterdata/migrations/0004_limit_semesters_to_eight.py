from django.db import migrations, models


SEMESTER_CHOICES = [(n, f"Semester {n}") for n in range(1, 9)]


class Migration(migrations.Migration):
    dependencies = [("masterdata", "0003_assignments")]

    operations = [
        migrations.AlterField(
            model_name="section",
            name="semester",
            field=models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES),
        ),
        migrations.AlterField(
            model_name="subject",
            name="semester",
            field=models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES),
        ),
        migrations.AlterField(
            model_name="student",
            name="semester",
            field=models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES),
        ),
        migrations.AddConstraint(
            model_name="section",
            constraint=models.CheckConstraint(
                condition=models.Q(semester__gte=1, semester__lte=8),
                name="section_semester_1_to_8",
            ),
        ),
        migrations.AddConstraint(
            model_name="subject",
            constraint=models.CheckConstraint(
                condition=models.Q(semester__gte=1, semester__lte=8),
                name="subject_semester_1_to_8",
            ),
        ),
        migrations.AddConstraint(
            model_name="student",
            constraint=models.CheckConstraint(
                condition=models.Q(semester__gte=1, semester__lte=8),
                name="student_semester_1_to_8",
            ),
        ),
    ]
