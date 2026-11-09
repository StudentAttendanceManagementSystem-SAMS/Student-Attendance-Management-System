# Student Attendance Management System (SAMS)

A role-based web application for recording, calculating, monitoring, and reporting student attendance. SAMS is developed for the Software Engineering course project at PES University using Python, Django, Django Templates, and SQLite.

## Features

### Authentication and access control
- Login/logout using Django authentication and sessions.
- Three application roles: Administrator, Faculty, and Student.
- Server-side role and ownership checks for protected workflows.
- Password hashing through Django's configured password hasher.
- Warning after repeated failed login attempts (the warning is not an account lockout).
- No-cache response headers for application pages to reduce the chance of stale protected pages appearing after logout.

### Master data
- Manage students, faculty, sections, subjects, subject-section mappings, and faculty assignments.
- Unique student USNs, faculty employee IDs, subject codes, and mapping/assignment constraints.
- Semester values are restricted to 1–8.

### Attendance
- Faculty can mark attendance for assigned subject-section combinations.
- Present/Absent records are unique per student, subject, and date.
- Reopening a saved session loads existing values for correction.
- Attendance correction is controlled by a configurable window (default 7 days).
- Attendance marking is restricted to the institution-wide configured active academic-term dates.
- Marking is blocked until both active-term dates are configured.

### Analytics and dashboards
- Subject-wise and overall attendance calculations, rounded to two decimal places.
- Overall attendance is a weighted aggregate of recorded classes.
- Section-wise, subject-wise, student history, and low-attendance views.
- Configurable minimum attendance threshold (default 75%).
- Role-specific dashboards for Administrator, Faculty, and Student.

### Profiles (additional project enhancement)
- A self-service profile page is available at `/profile/`.
- Student profile: date of birth/age, joining year, section/semester context, CGPA/SGPA, contact details, address, and parent/guardian details.
- Faculty profile: date of birth/age, date of joining, designation, department, email/contact details, address, and assigned teaching combinations.
- Administrator profile: date of birth/age, date of joining, designation, email/contact details, and address.
- Age is calculated from date of birth; it is not stored as a separate database field.
- Self-service forms expose only permitted fields. Students cannot edit USN, semester/section, CGPA, or SGPA through their own profile. Faculty cannot edit employee ID or employment/assignment fields through their own profile.
- Profile records are created on first profile visit. The profile models are also registered in Django Admin for authorized maintenance.

> Profile pages are an additional enhancement to the approved attendance scope. They should be recorded as an enhancement in the RTM unless the project supervisor formally adds them to the approved SRS.

## Technology stack

| Layer | Technology |
|---|---|
| Backend | Python 3 |
| Web framework | Django |
| Database | SQLite by default |
| UI | Django Templates, HTML, CSS, JavaScript |
| Authentication | Django authentication, sessions, custom role field |
| Data access | Django ORM |
| Automated tests | Django `TestCase` / `SimpleTestCase` |
| CI | GitHub Actions (`.github/workflows/django-tests.yml`) |

## Application roles

| Role | Main responsibilities |
|---|---|
| Administrator | Manage master data and assignments; configure attendance settings; review institution-wide reports; maintain profile records through authorized administration. |
| Faculty | View assigned classes; mark/correct attendance for assigned classes; review permitted reports; maintain own permitted profile details. |
| Student | View own dashboard, attendance and history; maintain own permitted personal/contact/guardian profile details. |

Role-based navigation is not the security boundary. Views and data access must enforce role and ownership checks on the server.

## Repository structure

```text
.
├── accounts/       Authentication, custom user model, role permissions
├── analytics/      Attendance calculations, reports, low-attendance logic
├── attendance/     Attendance records, marking, correction, settings
├── dashboard/      Administrator, Faculty, and Student dashboards
├── masterdata/     Students, faculty, sections, subjects, assignments
├── profiles/       Student, Faculty, and Administrator profile models/views
├── sams/           Django project settings, middleware, URL configuration
├── templates/      Django templates
├── static/         Project CSS, JavaScript, and static assets
├── docs/           User, setup, schema, test, demo, RTM, and handoff docs
├── .github/        GitHub Actions workflow
├── manage.py
└── requirements.txt
```

## Local installation

### Prerequisites
- Python 3.10 or later (the team has also tested in a Python 3.12 environment).
- `pip`
- Git

### Linux / macOS

```bash
git clone https://github.com/StudentAttendanceManagementSystem-SAMS/Student-Attendance-Management-System.git
cd Student-Attendance-Management-System

python3 -m venv venv
source venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Windows PowerShell

```powershell
git clone https://github.com/StudentAttendanceManagementSystem-SAMS/Student-Attendance-Management-System.git
cd Student-Attendance-Management-System

python -m venv venv
venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Sign in using the administrator credentials created by `createsuperuser`.

### Static files

During local development, Django serves configured static assets through `runserver`. For a deployment/collection step, ensure `STATIC_ROOT` is configured (the project setting uses `BASE_DIR / "staticfiles"`) and run:

```bash
python manage.py collectstatic --noinput
```

### Demo data

After migrations, generate the repeatable synthetic demo dataset:

```bash
python manage.py seed_demo
```

This creates/reuses 8 semester sections, 150 students, 40 faculty, semester-specific subjects/mappings/assignments, demo profile details, and attendance history. Default student/faculty demo password:

```text
SamsDemo@123
```

To select another password for newly created demo accounts:

```bash
python manage.py seed_demo --password 'YourStrongPassword'
```

The command does not reset passwords on accounts that already exist. See [`docs/DEMO_DATA.md`](docs/DEMO_DATA.md).

## Common commands

```bash
# Validate Django configuration
python manage.py check

# Confirm model changes have migrations
python manage.py makemigrations --check --dry-run

# Apply migrations
python manage.py migrate

# Run the complete test suite
python manage.py test

# Run a particular app's tests
python manage.py test accounts
python manage.py test masterdata
python manage.py test attendance
python manage.py test analytics
python manage.py test dashboard
python manage.py test profiles
```

Do not describe a test as passing unless the command output or CI result for the relevant commit confirms it. The current test evidence and outstanding retests are recorded in [`docs/TEST_REPORT.md`](docs/TEST_REPORT.md).

## First-time administrator configuration

1. Create the administrator using `createsuperuser`.
2. Sign in and create the required sections, subjects, students, faculty, and faculty assignments.
3. Open Attendance Settings.
4. Configure the minimum attendance percentage (default 75%), correction window (default 7 days), and both active academic-term dates.
5. Confirm the end date is on or after the start date.
6. Faculty can mark attendance only for dates inside the inclusive configured term range.

## Documentation

| Document | Purpose |
|---|---|
| [`docs/INSTALLATION.md`](docs/INSTALLATION.md) | Environment setup, migration, static files, and run commands |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | Role-specific application instructions |
| [`docs/DEMO_DATA.md`](docs/DEMO_DATA.md) | Synthetic demo dataset and account conventions |
| [`docs/DEMO_GUIDE.md`](docs/DEMO_GUIDE.md) | Suggested Admin → Faculty → Student demonstration |
| [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) | Main entities, keys, constraints, and relationships |
| [`docs/RTM.md`](docs/RTM.md) | Requirement-to-code/test traceability |
| [`docs/TEST_REPORT.md`](docs/TEST_REPORT.md) | Test execution evidence and outstanding retests |
| [`docs/PHASE3_TEST_PLAN_HANDOFF.md`](docs/PHASE3_TEST_PLAN_HANDOFF.md) | Manual test plan and acceptance handoff |
| [`docs/PROFILE_MODULE.md`](docs/PROFILE_MODULE.md) | Profile enhancement details |
| [`docs/SPRINT2_INTEGRATION_NOTES.md`](docs/SPRINT2_INTEGRATION_NOTES.md) | Sprint 2 integration notes |
| [`docs/schema-notes.md`](docs/schema-notes.md) | Normalization and academic-term design notes |

## Development workflow

- Create one branch per Jira item from `develop`, e.g. `feature/SAMS-40-attendance-threshold`.
- Prefix commits with the Jira key, e.g. `SAMS-40: validate attendance threshold`.
- Open pull requests against `develop`, request teammate review, and wait for required CI checks.
- Keep secrets, local databases, virtual environments, and real student data out of Git.
- Update the RTM and test report with actual test identifiers, run date, result, and evidence.

## Scope boundaries and future work

The system is a local Django application using SQLite and Django ORM. Cloud hosting, biometric attendance, AI/ML, microservices, SPA frontend, SMS/email notification delivery, and PDF/Excel report exports are not claimed as delivered features unless separately implemented and approved. These remain future scope.

---

Developed for academic purposes as part of the Software Engineering coursework at PES University.


## Testing and coverage

Install the coverage tool and run the complete suite with branch measurement:

```bash
pip install coverage
coverage erase
coverage run --rcfile=.coveragerc --branch manage.py test
coverage report --rcfile=.coveragerc --show-missing
coverage html --rcfile=.coveragerc
```

Open `htmlcov/index.html` to inspect missed lines and branch paths. GitHub Actions runs unit, integration, system, and coverage jobs on pushes and pull requests. See [`docs/TESTING_CI_COVERAGE.md`](docs/TESTING_CI_COVERAGE.md) for the four-person responsibility split and evidence checklist.

The current workflow provides Continuous Integration (CI). Automated Continuous Delivery/Deployment (CD) requires a selected hosting target and deployment secrets; it is not claimed as configured.
