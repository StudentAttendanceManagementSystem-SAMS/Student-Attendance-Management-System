# Student Attendance Management System (SAMS)

A web-based application for recording, calculating, monitoring, and reporting student attendance. SAMS is built with Python, Django, Django templates, and SQLite for the Software Engineering course project at PES University.

## Delivered capabilities

- Authenticated access with Administrator, Faculty, and Student roles.
- Role-specific dashboards and authorization checks.
- Management of students, faculty, sections, subjects, and faculty assignments.
- Faculty attendance marking and correction for assigned classes.
- Duplicate prevention for a student's subject/date attendance record.
- Attendance percentage calculation, including two-decimal rounding and handling of courses with no recorded classes.
- Administrator-configurable attendance threshold (default: 75%).
- Section-wise and subject-wise attendance reports for administrators.
- Low-attendance identification against the configured threshold.
- Automated Django tests and a GitHub Actions workflow.

> Documentation and test status: the repository's last observed `develop` CI run succeeded on 2026-10-28. This is a baseline result, not evidence that the Phase 3 test plan has been executed. See `docs/RTM.md` and `docs/PHASE3_TEST_PLAN_HANDOFF.md` for evidence status and remaining validation.

## Technology stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Django |
| Database | SQLite (default project configuration) |
| UI | Django templates, HTML, CSS, JavaScript |
| Authentication | Django authentication and sessions; custom user roles |
| Automated tests | Django `TestCase` / `SimpleTestCase` |
| CI | GitHub Actions (`.github/workflows/django-tests.yml`) |
| Planning and traceability | Jira, GitHub pull requests, RTM in `docs/RTM.md` |

## Roles and permissions

| Role | Main responsibilities |
|---|---|
| Administrator | Manage institution master data and assignments; configure the attendance threshold; view section-wise, subject-wise, and low-attendance reports. |
| Faculty | View assigned classes; mark and correct attendance for assigned classes; view relevant attendance history and low-attendance information within authorized scope. |
| Student | View their own attendance information and percentages. |

Access is enforced server-side. Hiding a link in the UI is not a substitute for authorization; role-specific views must reject unauthorized users.

## Repository layout

```text
.
├── accounts/       Authentication, user roles, role permissions, tests
├── analytics/      Attendance percentage services, reports, low-attendance logic, tests
├── attendance/     Attendance models, marking/editing, threshold configuration, tests
├── dashboard/     Role-specific dashboards and tests
├── docs/           Schema notes, user guide, RTM, Phase 3 test handoff
├── masterdata/     Students, faculty, sections, subjects, assignments, tests
├── sams/           Django project settings and URL configuration
├── static/         CSS, JavaScript, and static assets
├── templates/      Django templates
├── manage.py
├── requirements.txt
└── .github/workflows/django-tests.yml
```

## Setup and run locally

### Prerequisites

- Python 3 and `pip`
- Git
- A terminal (PowerShell on Windows, or a shell on macOS/Linux)

### Install

```bash
git clone https://github.com/StudentAttendanceManagementSystem-SAMS/Student-Attendance-Management-System.git
cd Student-Attendance-Management-System

# Windows PowerShell:
python -m venv venv
venv\Scripts\Activate.ps1

# macOS/Linux:
# python3 -m venv venv
# source venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser. Sign in with the superuser/admin credentials created during setup. Use institution-approved procedures to create the remaining users and master data.

### Run tests

```bash
python manage.py check
python manage.py test
```

The GitHub Actions workflow should also be checked on the pull request. Do not mark a new test run as passed until its actual output or CI result is available.

## Typical workflows

1. **Administrator setup:** create sections, subjects, student and faculty records; create/associate login accounts as supported by the UI; configure faculty assignments.
2. **Attendance:** faculty select an assigned subject/section and date, then mark each student present or absent. Reopening a previously marked session should load the saved values; submitting corrections should update existing records rather than create duplicates.
3. **Threshold:** an administrator configures the minimum attendance percentage. The model enforces a value from 0 to 100; the default is 75%.
4. **Reports:** administrators review section-wise and subject-wise reports. Low-attendance views identify eligible students below the configured threshold, subject to the view's role-specific scope.
5. **Students:** students sign in to review their own attendance information; they must not be able to access administrator reports or another student's private data.

See [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) for role-specific instructions and [`docs/PHASE3_TEST_PLAN_HANDOFF.md`](docs/PHASE3_TEST_PLAN_HANDOFF.md) for the validation handoff.

## Development workflow

- Create one branch per Jira item from `develop`, for example `feature/SAMS-40-attendance-threshold`.
- Prefix commits with the Jira key, for example `SAMS-40: validate attendance threshold`.
- Open pull requests against `develop`, summarize the change and test evidence, and obtain a teammate review before merging.
- Do not merge a pull request until required CI checks pass and the acceptance criteria are met.
- Update the RTM with test identifiers, execution date, result, and evidence link after running the tests. A test existing in the repository is not, by itself, proof that it passed in the current build.

## Project and traceability

- Course: UE24CS341A, Software Engineering, PES University.
- SRS reference for the documentation and test handoff work item: Project Plan WBS 10.0.
- The RTM is maintained in [`docs/RTM.md`](docs/RTM.md).
- The Phase 3 execution and handoff checklist is maintained in [`docs/PHASE3_TEST_PLAN_HANDOFF.md`](docs/PHASE3_TEST_PLAN_HANDOFF.md).

## Future scope

Potential extensions include report export, notifications, responsive UI improvements, QR-based attendance, and a production database deployment. These are future scope unless explicitly included in the approved requirements.

---

Developed for academic purposes as part of a college coursework submission.
