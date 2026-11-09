# Sprint 2 Integration Notes

## Included capabilities in the current candidate source

- Custom Django user model with Administrator, Faculty, and Student roles.
- Role-specific dashboards and navigation.
- Master-data management for students, faculty, sections, subjects, subject-section mappings, and faculty assignments.
- Semester restrictions from 1 through 8.
- Attendance marking and correction for assigned faculty subject-section combinations.
- Unique attendance per student, subject, and date.
- Institution-wide threshold, correction window, and active-term configuration.
- Attendance calculations, section/subject reports, student history, and low-attendance monitoring.
- Demo data command for eight semester sections, 150 students, 40 faculty, subject mappings, assignments, attendance history, and synthetic student/faculty profile details.
- Role-aware self-service profile pages for Student, Faculty, and Administrator.
- Profile models registered in Django Admin.
- No-cache middleware to discourage stale protected pages from being restored after logout.

## Profile enhancement

The Profile module is an additional enhancement beyond the original attendance requirements. See `PROFILE_MODULE.md` and the enhancement rows in `RTM.md`. The profile test suite had one reported form initialization error in its first shared run; a corrected form file was supplied, and the post-fix test result remains pending.

## Migrations

Relevant app migrations currently present in the candidate source include:
- `accounts.0001_custom_user`
- `masterdata.0001_section_subject` through `masterdata.0004_limit_semesters_to_eight`
- `attendance.0001_attendance_models` through `attendance.0003_attendanceconfig_academic_term`
- `profiles.0001_initial`

Apply migrations with `python manage.py migrate`. Confirm with `python manage.py showmigrations`.

## Required final verification

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
```

Also execute the manual cases in `PHASE3_TEST_PLAN_HANDOFF.md`, including role access, attendance term/correction boundaries, profile field permissions, student privacy, and browser logout behavior.

## Verification limitation

The packaging environment did not have Django available, so the final Django test suite, migrations, and browser-based manual checks were not run while preparing these documentation files. The developer's reported test evidence is captured in `TEST_REPORT.md`. Do not treat this candidate as fully test-passed until the target environment and CI confirm it.
