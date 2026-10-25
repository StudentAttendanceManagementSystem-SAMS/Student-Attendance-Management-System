from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import User


class UserRoleTests(TestCase):
    def test_user_is_saved_with_a_role(self):
        user = User.objects.create_user(
            username="fac1",
            password="pass12345",
            role=User.FACULTY,
        )
        self.assertEqual(user.role, "FACULTY")

    def test_role_is_required(self):
        with self.assertRaises(ValidationError) as ctx:
            User(username="norole").full_clean()
        self.assertIn("role", ctx.exception.message_dict)

    def test_invalid_role_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username="bad",
                    password="pass12345",
                    role="BOSS",
                )

    def test_superuser_gets_administrator_role(self):
        user = User.objects.create_superuser(
            username="root",
            password="pass12345",
        )
        self.assertEqual(user.role, User.ADMIN)