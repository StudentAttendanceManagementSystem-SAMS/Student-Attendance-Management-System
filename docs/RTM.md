# Requirements Traceability Matrix (RTM)

**System:** Student Attendance Management System (SAMS)  
**Primary source:** Approved SRS v1.0  
**Architecture source:** SAD v1.1  
**Planning source:** SAMS Sprint Plan and Jira backlog  
**Build:** Current local integration candidate; final commit SHA must be recorded in `TEST_REPORT.md`.

## Status definitions

- **Implemented / test present:** source implementation and a related automated test are present; this does not itself prove the test passed on the final build.
- **Partial:** some behavior exists, but implementation or verification is incomplete.
- **Pending execution:** test exists or manual verification is planned, but final run evidence is not available.
- **Enhancement:** additional feature not explicitly mapped to an approved SRS requirement; do not claim it as an SRS requirement without approval.

## Traceability matrix

| Requirement / source ID | Summary | Implementation | Verification source | Status |
|---|---|---|---|---|
| FR-AUTH-01, FR-AUTH-02 | Login and credential validation | `accounts/forms.py`, `accounts/urls.py`, `accounts/views.py` | `accounts/tests.py` login tests | Test execution on final build pending |
| FR-AUTH-03, FR-AUTH-04 | Session lifecycle and logout | Django sessions and logout view; `sams/settings.py` | `accounts/tests.py` logout tests; manual Back/logout test | Final execution pending |
| FR-AUTH-05 | Change own password | Accounts password-change route/templates | Password-change tests in `accounts/tests.py` | Final execution pending |
| FR-AUTH-06 | Warning after repeated failed login attempts | Custom authentication form/session counter | `accounts/tests.py` login warning tests | Final execution pending; warning is not a lockout |
| FR-RBAC-01–05 | One role per account and server-side authorization | `accounts/models.py`, permissions and app views | Accounts and app access tests | Final execution pending |
| FR-STU-01–06 | Student create/update/deactivate/list/filter and unique USN | `masterdata/models.py`, forms, views | `masterdata/tests.py` | Final execution pending |
| FR-FAC-01–05 | Faculty create/update/deactivate/list and assignments | `masterdata/models.py`, forms, views | `masterdata/tests.py` | Final execution pending |
| FR-CLS-01–04 | Section management, student association and dependency protection | `masterdata/models.py`, views | `masterdata/tests.py` | Final execution pending |
| FR-SUB-01–04 | Subject management and section mapping | `masterdata/models.py`, forms, views | `masterdata/tests.py` | Final execution pending |
| FR-ATT-01–04 | Assigned class selection, roster, attendance save, duplicate prevention | `attendance/views.py`, `attendance/models.py` | `attendance/tests.py` | Final execution pending |
| FR-ATT-05 | Correction within configured window | `AttendanceConfig.correction_window_days`; attendance view | Attendance correction/boundary tests | Final execution pending |
| FR-ATT-06 | Marked and modified timestamps | `Attendance.marked_at`, `Attendance.modified_at` | Attendance model tests | Final execution pending |
| FR-ATT-07 | Reject unconfigured/out-of-term dates and unauthorized assignment | `AttendanceConfig.term_start_date`, `term_end_date`; assignment checks | Attendance term/assignment tests | Final execution pending |
| FR-CALC-01–04 | Subject and weighted overall percentages; recalculation; two-decimal rounding | `analytics/services.py` | Analytics tests including overall calculation tests | Final execution pending |
| FR-REP-01 | Faculty subject/section report | Analytics report views/services | Analytics reporting tests | Final execution pending |
| FR-REP-02 | Admin section-wise and subject-wise reports | Analytics views/services/templates | `analytics/tests.py` | Final execution pending |
| FR-REP-03 | Student own attendance report | Student-scoped analytics/dashboard paths | Analytics and dashboard tests | Final execution pending |
| FR-REP-04 | Date-range report filtering | Analytics filter forms/views/services | `analytics/test_reporting_enhancements.py` | Final execution pending |
| FR-REP-05 | Student attendance history | Student history view/service with ownership scope | `analytics/test_reporting_enhancements.py` | Final execution pending |
| FR-LOW-01 | Configurable attendance threshold (default 75%) | `AttendanceConfig.threshold_percentage` and settings form | Attendance tests | Final execution pending |
| FR-LOW-02–04 | Subject/overall low-attendance detection and role scope | Analytics services/views | `analytics/test_below_threshold.py` and reporting tests | Final execution pending |
| FR-LOW-05 | Visual below-threshold highlighting | Analytics templates and CSS | Manual UI inspection | Manual verification pending |
| FR-DASH-01 | Administrator dashboard | `dashboard/views.py`, admin template | `dashboard/tests.py` | Final execution pending |
| FR-DASH-02 | Faculty dashboard | `dashboard/views.py`, faculty template | `dashboard/tests.py` | Final execution pending |
| FR-DASH-03 | Student dashboard | `dashboard/views.py`, student template | `dashboard/tests.py` | Final execution pending |
| NFR-001 | Performance targets for normal pages and attendance calculation | Django views/services and ORM query paths | Timed benchmark required; see `TEST_REPORT.md` | Pending measurement |
| NFR-002 | Persistence across application restarts | Django ORM/database persistence | Manual restart/persistence test | Pending execution |
| NFR-003 | Consistent and usable UI | Shared templates and CSS | Manual cross-role visual review | Pending final review |
| NFR-004 | Maintainable application structure | Django app separation and reusable services | Code review | Review pending |
| NFR-005 | Normalized schema | Django model relationships and constraints | `docs/DATABASE_SCHEMA.md`, schema review | Review pending |
| NFR-006 | Input validation | Django forms, validators, model/database constraints | App form/model tests | Final execution pending |
| SR-001 | Password hashing | Django authentication/password hashers | Accounts tests and configuration inspection | Final security review pending |
| SR-002 | Authenticated sessions | Django session/authentication middleware | Accounts tests and manual logout test | Final execution pending |
| SR-003 | Server-side role checks | Permission helpers and role-scoped views | Accounts and app permission tests | Final execution pending |
| SR-004 | CSRF protection | Django CSRF middleware and POST forms | Configuration/template review and tests | Final review pending |
| SR-005 | ORM-only data access | Django ORM model/query usage | Code review/search for raw SQL | Review pending |

## Additional project enhancement: role-based profiles

The Profile module was added as an enhancement in the current project iteration. Unless the approved SRS is formally revised, these rows are not represented as original SRS requirements.

| Enhancement ID | Behavior | Implementation | Automated/manual evidence | Status |
|---|---|---|---|---|
| ENH-PROF-01 | Student views own profile and academic details | `profiles/models.py`, `profiles/views.py`, student template | `ProfileAccessTests.test_student_sees_own_profile_and_academic_data` | Test was included; first reported run errored; corrected form supplied; retest pending |
| ENH-PROF-02 | Faculty views own employment/contact/teaching details | `profiles/views.py`, faculty profile template | `ProfileAccessTests.test_faculty_profile_shows_teaching_profile` | Retest pending |
| ENH-PROF-03 | Administrator views own profile | `profiles/views.py`, admin profile template | `ProfileAccessTests.test_admin_profile_is_created_on_first_visit` | Retest pending |
| ENH-PROF-04 | User cannot access another user's profile by changing an identifier | Self-only profile route at `/profile/` | `ProfileAccessTests.test_student_cannot_open_another_users_profile_by_id` | Retest pending |
| ENH-PROF-05 | Profile self-service form restricts editable fields by role | `profiles/forms.py` | Manual tampering/validation tests should be executed | Pending manual verification |
| ENH-PROF-06 | Profile data generated for demo student/faculty accounts | `masterdata/management/commands/seed_demo.py` | Demo seed command/manual inspection | Pending execution |

## Agreed design decisions

1. **Academic term:** one institution-wide active term is stored in `AttendanceConfig`; dates are configured together and the end date must be on or after the start date. Attendance is allowed only inside the inclusive date range.
2. **Correction window:** default 7 days, configurable from 0–365 days. Verify the boundary against the current view/tests before changing it.
3. **Overall attendance:** weighted aggregate (`total present / total recorded classes × 100`), not an unweighted average of subject percentages.
4. **No attendance data:** percentage is unavailable rather than zero.
5. **Repeated login failures:** warning behavior is not an account lockout.
6. **Semester range:** Section, Subject and Student semester values are restricted to 1–8.
7. **Profile enhancement:** age is derived from DOB; profile fields are role-specific; self-service editing is restricted; academic/master-data values are maintained through authorized paths.

## Verification record

Complete the following from the final candidate build. The detailed known test history is in `docs/TEST_REPORT.md`.

- Build/commit SHA:
- Python/Django versions:
- `python manage.py check`:
- `python manage.py makemigrations --check --dry-run`:
- `python manage.py migrate`:
- `python manage.py test`:
- GitHub Actions run URL:
- Manual test evidence:
- Open defects:
- Reviewer/test owner/sign-off:

A test file being present is not proof of a passing test. Only record Passed after observing the result on the relevant candidate commit.
