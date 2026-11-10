# Student Attendance Management System (SAMS)

A role-based web application for recording, calculating, monitoring, and reporting student attendance. SAMS is developed for the Software Engineering course project at PES University using Python, Django, Django Templates, and SQLite.

## Features

### Authentication and Access Control
* **Login/logout** utilizing Django authentication and sessions.
* **Three application roles:** Administrator, Faculty, and Student.
* Server-side role and ownership checks for protected workflows.
* Password hashing through Django's configured password hasher.
* Warning after repeated failed login attempts (note: this warning is not an account lockout).
* No-cache response headers for application pages to reduce the chance of stale protected pages appearing after logout.

### Master Data
* Manage students, faculty, sections, subjects, subject-section mappings, and faculty assignments.
* Unique student USNs, faculty employee IDs, subject codes, and mapping/assignment constraints.
* Semester values are strictly restricted to 1–8.

### Attendance
* Faculty can mark attendance for assigned subject-section combinations.
* Present/Absent records are unique per student, subject, and date.
* Reopening a saved session loads existing values for seamless correction.
* Attendance correction is controlled by a configurable window (default is 7 days).
* Attendance marking is restricted to the institution-wide configured active academic-term dates.
* Marking is blocked until both active-term dates are fully configured.

### Analytics and Dashboards
* Subject-wise and overall attendance calculations, rounded to two decimal places.
* Overall attendance is a weighted aggregate of recorded classes.
* Section-wise, subject-wise, student history, and low-attendance views.
* Configurable minimum attendance threshold (default 75%).
* Role-specific dashboards for Administrator, Faculty, and Student.

### Profiles (Additional Project Enhancement)
* A self-service profile page is available at `/profile/`.
* **Student profile:** Date of birth/age, joining year, section/semester context, CGPA/SGPA, contact details, address, and parent/guardian details.
* **Faculty profile:** Date of birth/age, date of joining, designation, department, email/contact details, address, and assigned teaching combinations.
* **Administrator profile:** Date of birth/age, date of joining, designation, email/contact details, and address.
* Age is calculated dynamically from date of birth; it is not stored as a separate database field.
* Self-service forms expose only permitted fields. Students cannot edit USN, semester/section, CGPA, or SGPA through their own profile. Faculty cannot edit employee ID or employment/assignment fields through their own profile.
* Profile records are created on first profile visit. The profile models are also registered in Django Admin for authorized maintenance.

> Profile pages are an additional enhancement to the approved attendance scope. They should be recorded as an enhancement in the RTM unless the project supervisor formally adds them to the approved SRS.

## Technology Stack

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

## Application Roles

| Role | Main responsibilities |
|---|---|
| Administrator | Manage master data and assignments; configure attendance settings; review institution-wide reports; maintain profile records through authorized administration. |
| Faculty | View assigned classes; mark/correct attendance for assigned classes; review permitted reports; maintain own permitted profile details. |
| Student | View own dashboard, attendance and history; maintain own permitted personal/contact/guardian profile details. |

*Role-based navigation is not the security boundary. Views and data access must enforce role and ownership checks on the server.*

## Repository Structure

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
├── test-evidence/  Test screenshots, coverage reports, and demo recordings
├── .github/        GitHub Actions workflow
├── manage.py
└── requirements.txt