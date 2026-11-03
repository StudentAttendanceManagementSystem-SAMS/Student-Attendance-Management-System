# Sprint 2 Security Review

## Scope

- Server-side role checks
- Faculty assignment ownership
- Student record isolation
- CSRF protection on state-changing requests
- ORM-only data access
- No credentials or real student data in Git

## Commands Executed

1. ORM and raw SQL search:
   `grep -RInE "cursor\(|\.raw\(|RawSQL|extra\(" accounts attendance analytics dashboard masterdata`

   Result: No matches found.

2. CSRF and unsafe HTML search:
   `grep -RInE "csrf_exempt|mark_safe|safe\}\}" accounts attendance analytics dashboard masterdata templates`

   Result: No matches found.

3. Role-boundary regression tests:
   `masterdata.tests.RoleBoundaryRegressionTests`

   Result: Blocked by an existing URL configuration error:
   `attendance.views.AttendanceConfigView` is missing.

## Findings

| Finding | File/route | Severity | Fix or rationale | Regression test |
|---|---|---|---|---|
| AttendanceConfigView missing | attendance/urls.py | Pending | Reported to attendance implementation owner | Existing attendance tests |
| Raw SQL search returned no matches | Project Python files | Informational | No matching patterns found | Not applicable |
| Unsafe HTML/CSRF exemption search returned no matches | Project Python files and templates | Informational | No matching patterns found | Further review pending |
| Role-boundary tests blocked | masterdata/tests.py | Pending | Waiting for URL configuration fix | RoleBoundaryRegressionTests |
| CSRF regression test | accounts/tests.py | Pending | Test added; execution awaits URL configuration fix | CsrfRegressionTests |
## Review Status

- Reviewer: Pranav Somashekar
- Commit: Pending
- Date: 2026-11-03
- Status: In progress