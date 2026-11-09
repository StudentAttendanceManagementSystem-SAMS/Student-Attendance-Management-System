"""Create a repeatable demo dataset for SAMS (8 semesters, 150 students, 40 faculty)."""

import random
from datetime import date, timedelta
from itertools import cycle

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from attendance.models import Attendance
from profiles.models import StudentProfile, FacultyProfile
from masterdata.models import (
    Faculty, FacultyAssignment, Section, Student, Subject, SubjectSection,
)


FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Ayaan", "Krishna",
    "Ishaan", "Shaurya", "Atharv", "Dhruv", "Kabir", "Rohan", "Ananya", "Diya",
    "Aadhya", "Ira", "Saanvi", "Anika", "Myra", "Aarohi", "Kavya", "Meera",
    "Sara", "Riya", "Nisha", "Ishita", "Prisha", "Tanvi", "Neha", "Sneha",
]
LAST_NAMES = [
    "Patel", "Sharma", "Reddy", "Iyer", "Nair", "Kulkarni", "Mehta", "Rao",
    "Shah", "Joshi", "Kumar", "Gupta", "Desai", "Pillai", "Shetty", "Mishra",
    "Verma", "Bhat", "Gowda", "Das", "Menon", "Chopra", "Jain", "Saxena",
]
SUBJECTS = [
    ("MAT", "Engineering Mathematics"),
    ("PHY", "Engineering Physics"),
    ("CHE", "Engineering Chemistry"),
    ("CSP", "Programming in C"),
    ("DMS", "Discrete Mathematical Structures"),
    ("DSA", "Data Structures"),
    ("OOP", "Object Oriented Programming"),
    ("DBM", "Database Management Systems"),
    ("OS", "Operating Systems"),
    ("CN", "Computer Networks"),
    ("SE", "Software Engineering"),
    ("CNS", "Computer Network Security"),
]


class Command(BaseCommand):
    help = "Populate SAMS with 8 semester sections, 150 demo students and 40 demo faculty."

    def add_arguments(self, parser):
        parser.add_argument("--password", default="SamsDemo@123", help="Password for generated student/faculty accounts.")

    @transaction.atomic
    def handle(self, *args, **options):
        rng = random.Random(20261103)
        password = options["password"]
        if len(password) < 8:
            self.stderr.write(self.style.ERROR("Demo password must contain at least 8 characters."))
            return

        # Create or reuse exactly one section for each of the eight semesters.
        sections = []
        for semester in range(1, 9):
            section, _ = Section.objects.get_or_create(
                name=f"DEMO-CSE-S{semester}-A",
                defaults={"semester": semester, "academic_year": "2026-27"},
            )
            sections.append(section)

        # 40 named faculty accounts; each account gets a profile and hashed password.
        faculties = []
        for number in range(1, 41):
            employee_id = f"DEMO-FAC-{number:03d}"
            username = employee_id
            first = FIRST_NAMES[(number * 3) % len(FIRST_NAMES)]
            last = LAST_NAMES[(number * 5) % len(LAST_NAMES)]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username.lower()}@sams-demo.edu", "role": User.FACULTY},
            )
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
            faculty, _ = Faculty.objects.get_or_create(
                employee_id=employee_id,
                defaults={
                    "user": user,
                    "name": f"{first} {last}",
                    "department": "Computer Science and Engineering",
                    "contact_no": f"9{rng.randrange(100000000, 999999999)}",
                },
            )
            faculties.append(faculty)
            FacultyProfile.objects.update_or_create(
                faculty=faculty,
                defaults={
                    "date_of_birth": date(1980 + number % 15, 1 + number % 12, 10 + number % 18),
                    "date_of_joining": date(2010 + number % 15, 7, 1),
                    "designation": "Assistant Professor" if number % 3 else "Associate Professor",
                    "personal_email": f"{username.lower()}@example.com",
                    "address": f"{100 + number} Demo Layout, Bengaluru, Karnataka",
                },
            )

        # 150 student records distributed across the eight semester sections.
        for number in range(1, 151):
            semester_index = (number - 1) % 8
            section = sections[semester_index]
            username = f"DEMO24CS{number:03d}"
            first = FIRST_NAMES[(number * 7) % len(FIRST_NAMES)]
            last = LAST_NAMES[(number * 11) % len(LAST_NAMES)]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username.lower()}@sams-demo.edu", "role": User.STUDENT},
            )
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
            student, _ = Student.objects.get_or_create(
                usn=username,
                defaults={
                    "user": user,
                    "name": f"{first} {last}",
                    "section": section,
                    "semester": section.semester,
                    "contact_no": f"9{rng.randrange(100000000, 999999999)}",
                },
            )
            StudentProfile.objects.update_or_create(
                student=student,
                defaults={
                    "date_of_birth": date(2003 + number % 5, 1 + number % 12, 1 + number % 27),
                    "joining_year": 2022 + (number % 3),
                    "current_cgpa": f"{7 + (number % 30) / 10:.2f}",
                    "current_sgpa": f"{7 + (number % 25) / 10:.2f}",
                    "address": f"{number} Demo Residency, Bengaluru, Karnataka",
                    "parent_name": f"{FIRST_NAMES[(number + 4) % len(FIRST_NAMES)]} {last}",
                    "parent_relationship": "Parent",
                    "parent_email": f"parent{number:03d}@example.com",
                    "parent_contact_no": f"8{rng.randrange(100000000, 999999999)}",
                },
            )

        # Five semester-specific subjects per semester, mapped to that semester's section.
        faculty_cycle = cycle(faculties)
        for semester, section in enumerate(sections, start=1):
            for subject_index in range(5):
                prefix, title = SUBJECTS[(semester + subject_index - 1) % len(SUBJECTS)]
                code = f"D-S{semester}-{prefix}"
                subject, _ = Subject.objects.get_or_create(
                    code=code,
                    defaults={"name": title, "semester": semester},
                )
                SubjectSection.objects.get_or_create(subject=subject, section=section)
                faculty = next(faculty_cycle)
                FacultyAssignment.objects.get_or_create(
                    faculty=faculty, subject=subject, section=section,
                )

        # Add reproducible attendance history for the last 20 weekdays so that
        # student, faculty and admin reports have meaningful demo content.
        attendance_rows = []
        demo_students = list(
            Student.objects.filter(usn__startswith="DEMO24CS")
            .select_related("section")
        )
        demo_subjects = list(
            Subject.objects.filter(code__startswith="D-S")
            .prefetch_related("assignments__faculty")
        )
        faculty_by_pair = {
            (assignment.subject_id, assignment.section_id): assignment.faculty
            for subject in demo_subjects
            for assignment in subject.assignments.all()
        }
        class_dates = []
        cursor = date.today()
        while len(class_dates) < 20:
            if cursor.weekday() < 5:
                class_dates.append(cursor)
            cursor -= timedelta(days=1)
        class_dates.reverse()

        for student in demo_students:
            student_subjects = [
                subject for subject in demo_subjects
                if subject.semester == student.semester
            ]
            for subject in student_subjects:
                faculty = faculty_by_pair.get((subject.pk, student.section_id))
                if faculty is None:
                    continue
                for class_date in class_dates:
                    attendance_rows.append(Attendance(
                        student=student,
                        subject=subject,
                        faculty=faculty,
                        date=class_date,
                        status=Attendance.PRESENT if rng.random() < (0.66 if student.pk % 10 == 0 else 0.88) else Attendance.ABSENT,
                    ))
        Attendance.objects.bulk_create(
            attendance_rows, batch_size=1000, ignore_conflicts=True,
        )

        self.stdout.write(self.style.SUCCESS(
            "Demo data ready: "
            f"{Section.objects.filter(name__startswith='DEMO-CSE-S').count()} semester sections, "
            f"{Student.objects.filter(usn__startswith='DEMO24CS').count()} students, "
            f"{Faculty.objects.filter(employee_id__startswith='DEMO-FAC-').count()} faculty, "
            f"{Subject.objects.filter(code__startswith='D-S').count()} subjects, "
            f"{Attendance.objects.filter(student__usn__startswith='DEMO24CS').count()} attendance records."
        ))
        self.stdout.write(f"Demo login password for generated student/faculty accounts: {password}")
        self.stdout.write("Student usernames: DEMO24CS001 to DEMO24CS150")
        self.stdout.write("Faculty usernames: DEMO-FAC-001 to DEMO-FAC-040")
