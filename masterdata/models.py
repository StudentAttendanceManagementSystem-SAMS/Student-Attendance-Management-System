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
