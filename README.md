# Student Attendance Management System (SAMS)

A web-based application to digitally manage and track student attendance, built as a college-level academic project using **Python, Django, and SQLite**.

SAMS replaces manual, register-based attendance tracking with role-specific dashboards for Administrators, Faculty, and Students — automatically calculating attendance percentages and flagging students who fall below a configurable minimum threshold.

---

## Table of Contents

- [Objectives](#objectives)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [User Roles](#user-roles)
- [Project Structure](#project-structure)
- [Database Schema (Overview)](#database-schema-overview)
- [Getting Started](#getting-started)
- [Project Team](#project-team)
- [Future Scope](#future-scope)
- [License](#license)

---

## Objectives

The Student Attendance Management System was built with the following objectives:

1. **Digitize attendance tracking** — replace manual, paper-register-based attendance with a reliable digital system.
2. **Provide role-based access** — give Administrators, Faculty, and Students distinct, permission-scoped views of the system.
3. **Centralize master data management** — allow Administrators to manage students, faculty, sections, and subjects from a single interface.
4. **Simplify attendance marking** — let Faculty mark attendance for their assigned subject-section combinations in a few clicks, with support for authorized corrections.
5. **Automate attendance calculation** — compute subject-wise and overall attendance percentages automatically, without manual tallying.
6. **Enable early intervention** — automatically identify and surface students whose attendance falls below a configurable minimum threshold (default 75%), so faculty can act before it becomes a problem.
7. **Support transparent reporting** — allow every role to generate or view attendance reports and history relevant to their scope (institution-wide, subject-wise, or personal).
8. **Ensure data integrity and security** — enforce authentication, role-based authorization, and server-side validation on all attendance-related operations.
9. **Keep the system practical for academic scope** — implement a functionally complete system using a straightforward, well-understood stack (Django + SQLite) without over-engineering (no biometrics, AI/ML, or cloud infrastructure).
10. **Provide a foundation for extension** — design a normalized data model and modular Django app structure that can be extended in future iterations (e.g., notifications, exports, mobile support).

---

## Key Features

- 🔐 Secure login and role-based access control (Administrator / Faculty / Student)
- 🧑‍🎓 Student, faculty, section, and subject management (CRUD)
- 📋 Faculty-side attendance marking with duplicate-entry prevention and an authorized edit window
- 📊 Automatic subject-wise and overall attendance percentage calculation
- ⚠️ Configurable low-attendance threshold with automatic flagging
- 📑 Attendance reports and attendance history, scoped by role
- 🏠 Role-specific dashboards summarizing relevant data at a glance
- ✅ Server-side data validation and error handling throughout

---

## Tech Stack

| Layer            | Technology                                  |
|-------------------|----------------------------------------------|
| Backend           | Python 3.x, Django                          |
| Database          | SQLite                                      |
| Frontend          | Django Templates, HTML, CSS, JavaScript     |
| Authentication    | Django's built-in auth & session framework  |
| Environment       | Local web application (Django dev server)   |

---

## User Roles

### 👤 Administrator
- Manage students, faculty, classes/sections, subjects, and user accounts
- Assign faculty to subject-section combinations
- Configure the minimum attendance threshold
- View institution-wide attendance records and reports

### 👨‍🏫 Faculty
- Log in securely and view assigned classes/subjects
- Mark and (within an authorized window) edit student attendance
- View attendance history for their subjects
- Generate/view attendance reports and low-attendance lists

### 🎓 Student
- Log in and view personal attendance records
- View subject-wise and overall attendance percentage
- View attendance history

---

## Project Structure

```
student-attendance-management-system/
├── manage.py
├── requirements.txt
├── sams/                   # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/               # Authentication & role-based access
├── students/                # Student management
├── faculty/                  # Faculty management
├── academics/               # Sections & subjects management
├── attendance/              # Attendance marking, calculation & reports
├── dashboard/               # Role-specific dashboards
├── templates/               # Shared HTML templates
├── static/                   # CSS, JS, static assets
└── db.sqlite3                # SQLite database (generated)
```

> Note: Folder names above reflect a suggested Django app breakdown based on the project's SRS and may be adapted during implementation.

---

## Database Schema (Overview)

| Entity              | Key Attributes                                                                 |
|----------------------|---------------------------------------------------------------------------------|
| User                | user_id (PK), username, password (hashed), role, email                         |
| Student             | student_id (PK), user_id (FK), USN, name, section_id (FK), semester, contact_no |
| Faculty             | faculty_id (PK), user_id (FK), employee_id, name, department, contact_no       |
| Section             | section_id (PK), section_name, semester, academic_year                         |
| Subject             | subject_id (PK), subject_code, subject_name, semester                          |
| Subject_Section     | id (PK), subject_id (FK), section_id (FK)                                      |
| Faculty_Assignment  | id (PK), faculty_id (FK), subject_id (FK), section_id (FK)                     |
| Attendance          | attendance_id (PK), student_id (FK), subject_id (FK), faculty_id (FK), date, status, marked_at, modified_at |
| Attendance_Config   | id (PK), threshold_percentage                                                  |

Full entity relationships and detailed field definitions are documented in the project's SRS document.

---

## Getting Started

### Prerequisites
- Python 3.x installed
- `pip` package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/student-attendance-management-system.git
cd student-attendance-management-system

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser (Administrator account)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

---

## Project Team

| USN              | Name                        |
|-------------------|-----------------------------|
| PES2UG24CS350     | Piyush A Patel              |
| PES2UG24CS310     | Neel Chandrakar             |
| PES2UG24CS331     | Nookala Sai Tushar Krishna  |
| PES2UG24CS364     | Pranav Somashekar           |

Developed as a mini-project for the DBMS / Software Engineering coursework at **PES University**.

---

## Future Scope

- Email/SMS notifications for low attendance
- Export of attendance reports to PDF/Excel
- Responsive, mobile-friendly interface
- Migration from SQLite to PostgreSQL for larger deployments
- QR-code-based attendance marking as a faster manual alternative

---

## License

This project is developed for academic purposes as part of a college coursework submission.
