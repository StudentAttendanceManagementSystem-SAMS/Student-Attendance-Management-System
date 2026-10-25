from django.conf import settings
from django.db import models


class Section(models.Model):
    name = models.CharField(max_length=30, unique=True)
    semester = models.PositiveSmallIntegerField()
    academic_year = models.CharField(max_length=9)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Subject(models.Model):
    code = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    semester = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile"
    )
    usn = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="students")
    semester = models.PositiveSmallIntegerField()
    contact_no = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ["usn"]

    def __str__(self):
        return f"{self.usn} - {self.name}"


class Faculty(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="faculty_profile"
    )
    employee_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ["employee_id"]
        verbose_name_plural = "faculty"

    def __str__(self):
        return f"{self.employee_id} - {self.name}"


class SubjectSection(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="section_links")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="subject_links")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["subject", "section"], name="unique_subject_section")
        ]

    def __str__(self):
        return f"{self.subject.code} in {self.section.name}"


class FacultyAssignment(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="assignments")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="assignments")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["faculty", "subject", "section"], name="unique_faculty_assignment"
            )
        ]

    def __str__(self):
        return f"{self.faculty.name}: {self.subject.code} ({self.section.name})"
