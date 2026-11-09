# Phase 3 Test Plan and Handoff

**Work item:** Documentation update and Phase 3 test handoff  
**Planning reference:** Project Plan WBS 10.0 / Sprint 2 quality work  
**Target branch:** `develop`  
**Disposition:** Test plan prepared; final execution and acceptance remain pending.

## 1. Objective

Validate SAMS against the approved SRS and the documented Profile enhancement. Coverage includes authentication, role authorization, master data, attendance, calculations, reports, dashboards, settings, profiles, security, persistence, and performance.

## 2. Entry criteria

- [ ] Candidate code is merged or available on the nominated test branch.
- [ ] Exact commit SHA is recorded.
- [ ] Dependencies install from `requirements.txt`.
- [ ] `python manage.py check` completes without issues.
- [ ] Migrations apply successfully and `makemigrations --check --dry-run` is clean.
- [ ] Synthetic test data is available.
- [ ] Active academic-term dates are configured for attendance tests.
- [ ] Approved SRS and acceptance criteria are available.
- [ ] CI workflow result is available for the candidate commit.

## 3. Automated test execution

Run:

```bash
python -m pip install -r requirements.txt
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
```

For targeted debugging:

```bash
python manage.py test accounts
python manage.py test masterdata
python manage.py test attendance
python manage.py test analytics
python manage.py test dashboard
python manage.py test profiles
```

Record exact command output, test count, failures/errors, date, environment, commit SHA, and CI URL in `TEST_REPORT.md`.

## 4. Manual test cases

| ID | Area | Scenario | Expected outcome | Status |
|---|---|---|---|---|
| P3-01 | Authentication | Admin login | Admin reaches authorized dashboard | Not run |
| P3-02 | Authentication | Faculty login | Faculty reaches authorized dashboard | Not run |
| P3-03 | Authentication | Student login | Student reaches authorized dashboard | Not run |
| P3-04 | Session | Logout then request protected page / use Back | New request requires login; no protected response is served to logged-out user | Not run |
| P3-05 | RBAC | Each role tries direct URL to disallowed page | Access denied/redirect; no protected data disclosure | Not run |
| P3-06 | Master data | Create valid and duplicate records | Valid records persist; duplicates are rejected | Not run |
| P3-07 | Semester | Try semester 0 and 9; use semesters 1–8 | Only semesters 1–8 are accepted | Not run |
| P3-08 | Faculty assignment | Faculty opens assigned and unassigned classes | Only assigned combinations are accessible | Not run |
| P3-09 | Attendance | Mark mixed present/absent roster | Correct unique rows are persisted | Not run |
| P3-10 | Attendance | Reopen and edit saved session | Saved values load; updates do not create duplicates | Not run |
| P3-11 | Attendance | Term unconfigured, before start, on start, on end, after end | Marking blocked when unconfigured/outside term; inclusive boundaries accepted | Not run |
| P3-12 | Attendance | Correction-window boundary and expired date | Edit behavior follows configured correction window | Not run |
| P3-13 | Calculation | Known present/held totals, rounding, no-record case | Correct two-decimal percentage; no-data is unavailable | Not run |
| P3-14 | Reports | Section and subject totals | Aggregates match source attendance records | Not run |
| P3-15 | Low attendance | Below, equal, above threshold and no-data students | Classification follows configured threshold and no-data rule | Not run |
| P3-16 | Student privacy | Student changes URL/identifier to request another student's data | Other student's private data is not returned | Not run |
| P3-17 | Student profile | View and edit permitted personal/guardian details | Own profile loads; permitted fields save; academic identifiers/scores remain protected | Not run |
| P3-18 | Faculty profile | View and edit permitted contact/personal details | Own profile loads; employment/assignment identifiers remain protected | Not run |
| P3-19 | Admin profile | View and update own profile | Own admin profile loads and permitted fields save | Not run |
| P3-20 | Profile validation | Future DOB, invalid email, invalid score or malformed values | Invalid values are rejected with field errors | Not run |
| P3-21 | Demo data | Run `seed_demo` twice | Expected demo records are created/reused; existing passwords and attendance are not reset | Not run |
| P3-22 | Persistence | Save attendance/profile, restart server, reload | Saved data persists | Not run |
| P3-23 | UI | Light/dark theme, navigation, profile cards, login/logout | Layout and contrast are usable across roles and supported viewport sizes | Not run |
| P3-24 | Performance | Measure login, dashboards, reports, attendance calculations | Timings recorded against approved NFR thresholds and repeatable dataset | Not run |

## 5. Test data

Use the generated synthetic demo dataset described in `DEMO_DATA.md`. Never use actual student or parent data in the repository or screenshots.

## 6. Defect handling

For each defect record:
- Defect key, title, severity and priority.
- Build SHA, environment, role, and synthetic record identifiers.
- Reproduction steps, expected and actual result.
- Redacted traceback, logs, or screenshot.
- Linked requirement/test case and Jira issue.
- Fix commit and retest result.

## 7. Exit criteria

- [ ] Full automated suite passes on final candidate commit.
- [ ] Required GitHub Actions checks pass.
- [ ] Manual scenarios have actual outcomes and evidence.
- [ ] Critical/high defects are fixed or formally accepted.
- [ ] RTM references verified tests and approved SRS IDs.
- [ ] Test report includes reproducible environment and results.
- [ ] README, installation guide, user guide, schema and demo guide reviewed.
- [ ] Reviewer and receiving test owner accept the handoff.

## 8. Handoff status

The profile test suite was reported as 3 passing and 1 error due to a form initializer referencing a field not present in the form. A corrected form file was supplied afterwards, but a post-fix test result has not yet been provided. The final full-suite result and CI status are also not supplied. Therefore, this handoff is prepared but not test-complete or signed off.
