# Generated for SAMS profile module.
import django.core.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("masterdata", "0004_limit_semesters_to_eight"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("joining_year", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("current_cgpa", models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ("current_sgpa", models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ("address", models.TextField(blank=True)),
                ("parent_name", models.CharField(blank=True, max_length=120)),
                ("parent_relationship", models.CharField(blank=True, max_length=40)),
                ("parent_email", models.EmailField(blank=True, max_length=254)),
                ("parent_contact_no", models.CharField(blank=True, max_length=15)),
                ("student", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="personal_profile", to="masterdata.student")),
            ],
            options={"ordering": ["student__usn"]},
        ),
        migrations.CreateModel(
            name="FacultyProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("date_of_joining", models.DateField(blank=True, null=True)),
                ("designation", models.CharField(blank=True, max_length=100)),
                ("personal_email", models.EmailField(blank=True, max_length=254)),
                ("address", models.TextField(blank=True)),
                ("faculty", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="personal_profile", to="masterdata.faculty")),
            ],
            options={"ordering": ["faculty__employee_id"]},
        ),
        migrations.CreateModel(
            name="AdminProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("date_of_joining", models.DateField(blank=True, null=True)),
                ("designation", models.CharField(blank=True, max_length=100)),
                ("contact_no", models.CharField(blank=True, max_length=15)),
                ("address", models.TextField(blank=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="admin_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
