# Requirements Traceability Matrix (RTM)

**Work item:** Documentation update and Phase 3 test handoff
**SRS reference:** Project Plan WBS 10.0
**Repository baseline:** `develop`, observed CI run on 2026-10-28 (successful)
**Status note:** This RTM records the current automated test inventory and the known CI baseline. It does **not** claim that the final Phase 3 test suite has been executed. Update Result and Evidence after execution.

## Result definitions

- **Implemented / test present:** corresponding code and automated test names were found in the repository.
- **Baseline CI pass:** the most recently observed `develop` GitHub Actions run passed; this is not a result for this documentation change.
- **Not yet executed (Phase 3):** execution of the final Phase 3 test plan is still required.
- **SRS ID confirmation required:** functional labels below are descriptive unless an exact approved SRS identifier was visible in the work item/repository. Confirm IDs against the controlled SRS before sign-off.

## Traceability matrix

| Requirement / feature | SRS reference | Test case(s) / automated evidence | Expected result | Current evidence status | Phase 3 result |
|---|---|---|---|---|---|
| Authentication and session lifecycle | Confirm exact SRS ID | `accounts/tests.py`: `LoginTests.test_valid_login_creates_session`, `test_invalid_login_shows_error_and_creates_no_session`; `LogoutTests.test_logout_ends_the_session`, `test_protected_page_redirects_to_login_after_logout`, `test_session_expires_after_two_hours_of_inactivity` | Valid credentials create a session; invalid credentials do not; logout/session expiry protect pages | Tests present; last `develop` CI baseline passed | Not yet executed for Phase 3 |
| Role model and authorization | Confirm exact SRS ID | `accounts/tests.py`: `UserRoleTests` tests; `attendance/tests.py`: `AttendanceConfigViewTests.test_faculty_cannot_access_threshold_settings`; `analytics/tests.py`: `ReportViewTests.test_faculty_and_students_cannot_open_report_pages`; `analytics/test_below_threshold.py`: role-access tests | Users have valid roles and unauthorized roles cannot use restricted pages | Tests present; last `develop` CI baseline passed | Not yet executed for Phase 3 |
| Master data uniqueness and validation | Confirm exact SRS ID | `masterdata/tests.py`: `MasterDataModelTests` uniqueness tests; `StudentPageTests.test_duplicate_usn_is_rejected_with_a_clear_message`, `test_usn_is_stored_in_upper_case`; `SubjectPageTests.test_duplicate_subject_code_is_rejected`; `AssignmentPageTests.test_duplicate_assignment_is_rejected` | Invalid duplicates are rejected and valid records persist | Tests present; last `develop` CI baseline passed | Not yet executed for Phase 3 |
| Student/faculty account creation and master data UI | Confirm exact SRS ID | `masterdata/tests.py`: `StudentPageTests.test_create_student_also_creates_login_account`; `FacultyPageTests.test_create_faculty_also_creates_a_login_account`; section/subject/assignment page tests | Related account/data is created and appears in relevant UI | Tests present; last `develop` CI baseline passed | Not yet executed for Phase 3 |
| Faculty class selection and assignment scope | Confirm exact SRS ID | `attendance/tests.py`: `ClassSelectionTests.test_only_own_assignments_are_listed`, `test_valid_selection_redirects_to_roster`, `test_faculty_without_assignments_sees_message`; `RosterViewTests` | Faculty sees assigned classes and the expected roster; invalid selection fails safely | Tests present; last `develop` CI baseline passed | Not yet executed for Phase 3 |
| Attendance marking, correction, and integrity | Confirm exact SRS ID | `attendance/tests.py`: `SaveAttendanceTests` tests; `DuplicateMarkingTests` tests; `AttendanceEdgeCaseTests` tests; `AttendanceModelTests.test_duplicate_student_subject_date_is_rejected` | Attendance is linked to correct faculty; repeat submissions update rather than duplicate; data remains scoped to subject/date | Tests present; last `develop` CI baseline passed | Not yet executed for Phase 3 |
| Configurable attendance threshold | Confirm exact SRS ID | `attendance/tests.py`: `AttendanceModelTests.test_default_threshold_is_75`; `AttendanceConfigViewTests.test_default_threshold_is_displayed_to_admin`, `test_admin_can_update_threshold_and_value_persists`, `test_invalid_threshold_is_rejected` | Default is 75%; authorized admin changes persist; out-of-range values are rejected | Tests present; last `develop` CI baseline passed | Not yet executed for Phase 3 |
| Attendance percentage calculation | Confirm exact SRS ID | `analytics/tests.py`: `PercentageTests.test_calculates_percentage`, `test_returns_none_when_no_classes_were_recorded`, `test_rounds_to_two_decimal_places` | Percentages are calculated, missing data is handled, and rounding is consistent | Tests present; last `develop` CI baseline passed | Not yet executed for Phase 3 |
| Administrator section-wise reporting | `SAMS-F-032` only if confirmed by controlled SRS; work item description states institution-wide reports by section and subject | `analytics/tests.py`: `SectionWiseReportTests.test_report_calculates_each_section_separately`, `test_section_without_attendance_returns_none_percentage`; `ReportViewTests` | Aggregates are calculated independently per section; no-attendance values are handled | Tests present; last `develop` CI baseline passed | Not yet executed for Phase 3 |
| Administrator subject-wise reporting across sections | Work item references `SAMS-F-032`; verify exact scope/ID against SRS | `analytics/tests.py`: `SubjectWiseReportTests.test_subject_report_aggregates_across_sections`, `test_subject_without_attendance_returns_none_percentage`; `ReportViewTests` | Subject report aggregates applicable records across sections and handles no-attendance data | Tests present; last `develop` CI baseline passed | Not yet executed for Phase 3 |
| Students below configured attendance threshold | Confirm exact SRS ID | `analytics/test_below_threshold.py`: `BelowThresholdServiceTests.test_identifies_students_below_threshold`, `test_student_exactly_at_threshold_is_excluded`, `test_student_without_attendance_is_excluded`; `BelowThresholdViewTests` role/scope tests | Only students strictly below the configured threshold are flagged; exact-threshold and no-data cases are excluded as designed | Tests present; last `develop` CI baseline passed | Not yet executed for Phase 3 |
| Role-specific dashboards | Confirm exact SRS ID | `dashboard/tests.py` (inspect and map detailed test names during Phase 3 execution) | Each role receives the intended dashboard and no unauthorized data | Test module exists; detailed case mapping pending | Not yet executed for Phase 3 |
| README, User Guide, RTM, and Phase 3 handoff updated | Project Plan WBS 10.0 | Documentation review checklist in `docs/PHASE3_TEST_PLAN_HANDOFF.md` | Docs reflect the delivered system and clearly distinguish verified results from pending tests | Drafts prepared; branch/PR/CI still required | Pending review and merge |

## Sign-off fields

Fill these fields after the final test execution:

- **Build/commit under test:** `TBD`
- **Test execution date and environment:** `TBD`
- **Automated test command and outcome:** `TBD`
- **Manual test execution record:** `TBD`
- **Open defects / severity:** `TBD`
- **Evidence links (CI run, screenshots/logs):** `TBD`
- **Tester:** `TBD`
- **Reviewer / approval:** `TBD`
- **Phase 3 handoff accepted by:** `TBD`

## Change control

Do not replace `Not yet executed` with `Pass` merely because a test method exists or an earlier commit passed CI. Update each row with the actual result, run/commit identifier, and evidence link.
