from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", "ADMIN")
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    ADMIN = "ADMIN"
    FACULTY = "FACULTY"
    STUDENT = "STUDENT"

    ROLE_CHOICES = [
        (ADMIN, "Administrator"),
        (FACULTY, "Faculty"),
        (STUDENT, "Student"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    objects = UserManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=["ADMIN", "FACULTY", "STUDENT"]),
                name="accounts_user_role_valid",
            )
        ]

    def __str__(self):
        return f"{self.get_username()} ({self.get_role_display()})"