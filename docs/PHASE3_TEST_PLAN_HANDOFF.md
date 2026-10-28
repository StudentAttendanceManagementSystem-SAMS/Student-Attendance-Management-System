# Phase 3 Test Plan Handoff

**Work item:** Update README, User Guide, RTM, and hand off to the Phase 3 test plan
**SRS / planning reference:** Project Plan WBS 10.0
**Target integration branch:** `develop`
**Handoff status:** Ready for test planning; execution and sign-off pending

## 1. Objective

Validate the delivered Student Attendance Management System (SAMS) against its functional requirements and acceptance criteria. The handoff covers authentication, role authorization, master data, attendance marking/correction, threshold configuration, percentage calculation, reports, low-attendance detection, dashboards, and documentation.

## 2. Baseline and constraints

- The repository contains Django automated tests under `accounts/`, `masterdata/`, `attendance/`, `analytics/`, and `dashboard/`.
- The most recent observed GitHub Actions run for `develop` completed successfully on 2026-10-28. This is a baseline only.
- The final Phase 3 build has not been tested as part of this handoff.
- Exact SRS IDs must be reconciled with the approved SRS; the work item explicitly references Project Plan WBS 10.0 and the related reporting work references `SAMS-F-032`.
- Use a disposable test database and synthetic test records. Do not use production credentials or real student data.

## 3. Entry criteria

- [ ] Documentation branch contains README, user guide, RTM, and this handoff.
- [ ] PR targets `develop` and includes the Jira work item key.
- [ ] Required reviewers have reviewed the changes.
- [ ] Required CI workflow is green for the PR commit.
- [ ] Test environment can install `requirements.txt`, apply migrations, and run `python manage.py check`.
- [ ] Test data and expected outcomes are available.
- [ ] Approved SRS/requirements are available to confirm exact requirement IDs.

## 4. Test execution

### Automated suite

From the repository root, with the project virtual environment activated:

```bash
python -m pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py test
```

Record the commit SHA, date/time, environment/Python version, command, exit status, and CI run URL. Investigate and log failures before sign-off.

### Manual functional and role checks

| ID | Scenario | Steps / setup | Expected outcome | Result |
|---|---|---|---|---|
| P3-01 | Administrator login | Sign in using an authorized admin test account | Admin reaches the intended dashboard and admin functions are available | Not run |
| P3-02 | Invalid login/logout | Try invalid credentials; sign in then log out and revisit a protected page | Invalid login is rejected; logged-out user cannot continue using protected pages | Not run |
| P3-03 | Role access control | Sign in as each role and attempt pages outside that role's permissions, including direct URLs | Unauthorized access is denied/redirected; no protected data is exposed | Not run |
| P3-04 | Master data validation | Create valid section, subject, student, faculty, and assignment; try duplicate unique identifiers | Valid data persists; duplicates/invalid values show a useful error and do not corrupt data | Not run |
| P3-05 | Faculty assignment scope | Use a faculty account with one assignment and another without assignments | Faculty sees only assigned class options; unassigned faculty gets a clear empty state | Not run |
| P3-06 | Mark attendance | Open an assigned class/date and mark a mixed present/absent roster | One record per student/subject/date is saved and linked to the correct faculty | Not run |
| P3-07 | Correct attendance | Reopen the same class/date, change statuses, submit again | Existing values load and updates do not create duplicate records | Not run |
| P3-08 | Attendance data integrity | Attempt invalid status/date/class selection and cross-subject changes | Invalid requests fail safely; unrelated subject records remain unchanged | Not run |
| P3-09 | Threshold settings | Check default; set a valid threshold; try values outside 0–100 and use a non-admin account | Default is 75%; valid change persists; invalid change is rejected; unauthorized access is denied | Not run |
| P3-10 | Percentage edge cases | Check a known numerator/denominator, rounding boundary, and no-record case | Expected percentage/rounding is correct; no-data case is represented as unavailable per design | Not run |
| P3-11 | Section-wise report | Create attendance across at least two sections and compare report totals with source records | Each section's aggregate is correct and isolated from other sections | Not run |
| P3-12 | Subject-wise report | Use the same subject across multiple sections where supported; compare totals with source records | Subject aggregation follows the approved requirement and does not double-count records | Not run |
| P3-13 | Below-threshold report | Prepare students below, exactly at, above threshold, and with no attendance | Below-threshold inclusion matches specification; exact-threshold and no-data behavior match design | Not run |
| P3-14 | Student privacy | Sign in as a student and try to access another student's record or admin report URL | Student can see only their own permitted information | Not run |
| P3-15 | Dashboard smoke test | Visit each role dashboard using its corresponding test account | Correct dashboard loads without server errors or cross-role data exposure | Not run |
| P3-16 | Documentation review | Follow README setup, each role's guide, and compare RTM rows to tests and SRS | Instructions are reproducible, traceability is accurate, unknown IDs/results remain explicitly pending | Not run |

## 5. Defect handling

For each failure, create a Jira defect with:

- Unique defect key and concise title.
- Environment, tested commit SHA, role, and test data identifiers (synthetic only).
- Reproduction steps, expected result, actual result, logs/screenshots with secrets removed.
- Severity/priority, assignee, status, and linked requirement/test case.
- Retest result and evidence after the fix.

Do not mark a failing case as passed because a workaround exists unless the approved acceptance criteria explicitly allow it.

## 6. Exit criteria

- [ ] All automated tests pass on the candidate PR commit and required CI is green.
- [ ] All planned manual cases have an actual result and evidence.
- [ ] Critical/high-severity defects are fixed or formally accepted by the project owner.
- [ ] RTM rows are linked to confirmed SRS IDs, executed test cases, and evidence.
- [ ] README and user guide accurately describe behavior in the delivered build.
- [ ] Reviewer approval is recorded and the PR is merged to `develop`.
- [ ] Phase 3 tester/owner accepts the handoff.

## 7. Handoff checklist

- [ ] README reflects current setup, architecture, features, roles, testing, and workflow.
- [ ] User guide covers administrator, faculty, and student tasks and troubleshooting.
- [ ] RTM identifies requirement, test coverage, result, and evidence without fabricated pass claims.
- [ ] Test runner and CI workflow verified on the final candidate commit.
- [ ] Open defects and known limitations handed to the Phase 3 test owner.
- [ ] Reviewer and receiving test owner recorded.

## 8. Current handoff disposition

**Disposition: Ready for Phase 3 planning, not yet accepted as test-complete.**

The documentation content is prepared for review. Phase 3 execution, final result entry, PR review/merge, and handoff acceptance remain outstanding until supported by repository and CI evidence.
