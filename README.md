# Student Attendance Management System (SAMS)

A web-based application to digitally manage and track student attendance, built as a college project using **Python, Django and SQLite**.

SAMS replaces manual, register-based attendance with role-specific dashboards for Administrators, Faculty and Students. It calculates attendance percentages automatically and flags students who fall below a configurable minimum (default 75%).

Course: UE24CS341A, Software Engineering, PES University

---

## Objectives

1. **Digitize attendance tracking** and replace paper registers.
2. **Provide role-based access** so Administrators, Faculty and Students each see only what they should.
3. **Centralize master data** (students, faculty, sections, subjects) in one interface.
4. **Simplify attendance marking** for faculty, with authorized corrections.
5. **Automate attendance calculation**, subject-wise and overall.
6. **Enable early intervention** by flagging students below the attendance threshold.
7. **Support transparent reporting** scoped to each role.
8. **Ensure data integrity and security** with authentication, server-side authorization and validation.
9. **Keep the scope practical** for an academic project: Django and SQLite, no over-engineering.
10. **Allow future extension** through a normalized schema and modular Django apps.

---

## Key Features

- Secure login and role-based access control (Administrator, Faculty, Student)
- Student, faculty, section and subject management
- Attendance marking with duplicate prevention and an authorized edit window
- Automatic subject-wise and overall attendance percentages
- Configurable low-attendance threshold with automatic flagging
- Attendance reports and history, scoped by role
- Role-specific dashboards
- Server-side validation and error handling

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Django |
| Database | SQLite |
| Frontend | Django Templates, HTML, CSS, JavaScript |
| Authentication | Django auth and sessions |
| Testing and CI | Django TestCase, GitHub Actions |
| Planning | Jira (Scrum), GitHub |

---

## User Roles

- **Administrator:** manages students, faculty, sections, subjects and accounts; assigns faculty to classes; sets the attendance threshold; views all reports.
- **Faculty:** views assigned classes, marks and corrects attendance, views history and reports, sees low-attendance students.
- **Student:** views personal attendance, subject-wise and overall percentages, and history.

---

## Project Structure

```
Student-Attendance-Management-System/
├── manage.py
├── requirements.txt
├── sams/            Django project settings
├── accounts/        Login, roles and access control
├── masterdata/      Students, faculty, sections, subjects, assignments
├── attendance/      Attendance marking and editing
├── analytics/       Percentage calculation, reports, low-attendance
├── dashboard/       Role-specific dashboards
├── templates/       Shared HTML templates
└── static/          CSS, JS and static files
```

---

## Database Schema (Overview)

| Entity | Key attributes |
|---|---|
| User | user_id (PK), username, password (hashed), role, email |
| Student | student_id (PK), user_id (FK), USN, name, section_id (FK), semester, contact_no |
| Faculty | faculty_id (PK), user_id (FK), employee_id, name, department, contact_no |
| Section | section_id (PK), section_name, semester, academic_year |
| Subject | subject_id (PK), subject_code, subject_name, semester |
| Subject_Section | id (PK), subject_id (FK), section_id (FK) |
| Faculty_Assignment | id (PK), faculty_id (FK), subject_id (FK), section_id (FK) |
| Attendance | attendance_id (PK), student_id (FK), subject_id (FK), faculty_id (FK), date, status, marked_at, modified_at |
| Attendance_Config | id (PK), threshold_percentage |

Full details are in the SRS and SAD documents.

---

## Getting Started

Requires Python 3 and pip.

```bash
git clone https://github.com/StudentAttendanceManagementSystem-SAMS/Student-Attendance-Management-System.git
cd Student-Attendance-Management-System

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

---

## Team Workflow

- **Branches:** `master` is stable and only receives `develop` at the end of a sprint. `develop` is the integration branch. Each Jira item gets its own branch, for example `feature/SAMS-14-login`.
- **Commits:** every commit message starts with the Jira key, for example `SAMS-14: add login view and template`.
- **Pull requests:** open into `develop`, include the Jira key in the title, and get one teammate's review before merging.
- **Planning:** two Scrum sprints tracked in Jira. Sprint 1 covers login, roles, master data and attendance marking. Sprint 2 covers reports, low-attendance monitoring, dashboards and quality work.

---

## Project Team

| USN | Name | Area |
|---|---|---|
| PES2UG24CS350 | Piyush A Patel | Attendance Engine |
| PES2UG24CS310 | Neel Chandrakar | Master Data Management |
| PES2UG24CS331 | Nookala Sai Tushar Krishna | Authentication and Security |
| PES2UG24CS364 | Pranav Somashekar | Analytics, Reporting and Dashboards |

---

## Future Scope

- Email or SMS notifications for low attendance
- Export of reports to PDF or Excel
- Responsive, mobile-friendly interface
- Migration from SQLite to PostgreSQL
- QR-code-based attendance marking

---

Developed for academic purposes as part of a college coursework submission.
