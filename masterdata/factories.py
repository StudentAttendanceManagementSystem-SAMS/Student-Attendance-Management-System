from itertools import count

from django.contrib.auth.hashers import make_password

from accounts.models import User

from .models import Faculty, FacultyAssignment, Section, Student, Subject

PASSWORD = "pass12345"
PASSWORD_HASH = make_password(PASSWORD)
_counter = count(1)


def make_section(**kwargs):
    n = next(_counter)
    defaults = {"name": f"CSE-{n}A", "semester": 3, "academic_year": "2026-27"}
    defaults.update(kwargs)
    return Section.objects.create(**defaults)


def make_subject(**kwargs):
    n = next(_counter)
    defaults = {"code": f"CS{n:03d}", "name": f"Subject {n}", "semester": 3}
    defaults.update(kwargs)
    return Subject.objects.create(**defaults)


def make_student(section=None, **kwargs):
    n = next(_counter)
    section = section or make_section()
    user = User.objects.create(username=f"student{n}", password=PASSWORD_HASH, role=User.STUDENT)
    defaults = {
        "user": user,
        "usn": f"PES2UG24CS{n:03d}",
        "name": f"Student {n}",
        "section": section,
        "semester": section.semester,
        "contact_no": "9876543210",
    }
    defaults.update(kwargs)
    return Student.objects.create(**defaults)


def make_faculty(**kwargs):
    n = next(_counter)
    user = User.objects.create(username=f"faculty{n}", password=PASSWORD_HASH, role=User.FACULTY)
    defaults = {
        "user": user,
        "employee_id": f"FAC{n:03d}",
        "name": f"Faculty {n}",
        "department": "Computer Science",
        "contact_no": "9876500000",
    }
    defaults.update(kwargs)
    return Faculty.objects.create(**defaults)


def make_assignment(faculty=None, subject=None, section=None):
    return FacultyAssignment.objects.create(
        faculty=faculty or make_faculty(),
        subject=subject or make_subject(),
        section=section or make_section(),
    )
