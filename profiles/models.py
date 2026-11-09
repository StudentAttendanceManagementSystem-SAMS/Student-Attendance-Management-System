from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class StudentProfile(models.Model):
    student = models.OneToOneField(
        "masterdata.Student", on_delete=models.CASCADE, related_name="personal_profile"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    joining_year = models.PositiveSmallIntegerField(null=True, blank=True)
    current_cgpa = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    current_sgpa = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    address = models.TextField(blank=True)
    parent_name = models.CharField(max_length=120, blank=True)
    parent_relationship = models.CharField(max_length=40, blank=True)
    parent_email = models.EmailField(blank=True)
    parent_contact_no = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ["student__usn"]

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __str__(self):
        return f"Student profile: {self.student.usn}"


class FacultyProfile(models.Model):
    faculty = models.OneToOneField(
        "masterdata.Faculty", on_delete=models.CASCADE, related_name="personal_profile"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    personal_email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["faculty__employee_id"]

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __str__(self):
        return f"Faculty profile: {self.faculty.employee_id}"


class AdminProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="admin_profile"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    contact_no = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __str__(self):
        return f"Administrator profile: {self.user.username}"
