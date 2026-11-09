# SAMS Test Execution Report

**Purpose:** Record reproducible automated and manual test evidence for the delivered candidate.  
**Status:** In progress — do not interpret planned cases as passed.

## 1. Test environment record

| Field | Value |
|---|---|
| Project | Student Attendance Management System (SAMS) |
| Framework | Django 6.1.2 (reported by the developer environment) |
| Python | Python 3.12 (reported by the developer environment) |
| Database | SQLite |
| Environment | Local Linux development environment / virtual environment |
| Tested build | Profile module integration candidate; exact Git commit SHA not supplied |
| Report date | 2026-11-03 |
| Tester | Project team; individual execution details to be filled in |

## 2. Automated test evidence currently known

The following result was shared from the developer's terminal:

Command:

```bash
python manage.py check
python manage.py test profiles
```

Observed output:
- Django system check: no issues (0 silenced).
- `profiles` test suite discovered 4 tests.
- Three tests passed.
- One test errored: `ProfileAccessTests.test_student_sees_own_profile_and_academic_data`.
- Exception: `KeyError: 'joining_year'` in `profiles/forms.py` while the form initializer attempted to set help text for a field not included in the form.

A corrected `profiles/forms.py` file was subsequently supplied to remove access to non-form fields. **A rerun result after applying that correction has not yet been provided.** Therefore, the four profile tests must remain marked Pending retest, not Passed.

| Test command / suite | Observed result | Current disposition |
|---|---|---|
| `python manage.py check` | Passed; no issues reported in the shared run | Passed for that run only; rerun on final commit |
| `python manage.py test profiles` before form correction | 3 passed, 1 error | Failed (initial run); retest pending after correction |
| `python manage.py test` full suite | No final output supplied | Not run / evidence not supplied |
| `python manage.py makemigrations --check --dry-run` | No final output supplied for the profile-integrated candidate | Pending |
| GitHub Actions final candidate CI | No final run URL/result supplied | Pending |

## 3. Required automated retest

After applying the corrected profile form file and all final changes, run:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test profiles
python manage.py test
```

Record the exact output, test count, failures/errors, date, commit SHA, and CI URL. Do not overwrite the historical failed run above; append the retest as a new execution entry.

## 4. Manual test checklist

Set each case to `Not run` until it has been executed on the final candidate.

| ID | Scenario | Expected result | Result / evidence |
|---|---|---|---|
| MAN-01 | Administrator login and dashboard | Administrator reaches the admin dashboard and sees authorized navigation | Not run |
| MAN-02 | Faculty login and dashboard | Faculty sees only authorized teaching and report functions | Not run |
| MAN-03 | Student login and dashboard | Student sees own attendance summary and authorized links | Not run |
| MAN-04 | Logout and protected-page Back navigation | Session ends; a fresh request for a protected page redirects to login | Not run |
| MAN-05 | Admin attendance configuration | Threshold, correction window, and both term dates save and persist | Not run |
| MAN-06 | Attendance term boundary | Dates inside inclusive term accepted; dates outside term rejected | Not run |
| MAN-07 | Faculty assignment scope | Faculty can open only assigned subject-section combinations | Not run |
| MAN-08 | Attendance create/update | Roster values save; reopening loads values; correction updates existing rows | Not run |
| MAN-09 | Correction window | Editing is allowed/denied according to configured boundary | Not run |
| MAN-10 | Student privacy | Student cannot view another student's attendance/profile by URL manipulation | Not run |
| MAN-11 | Faculty profile | Faculty sees own profile and permitted fields can be updated | Not run |
| MAN-12 | Student profile | Student sees own profile; protected academic fields cannot be changed through self-service | Not run |
| MAN-13 | Admin profile | Admin sees and updates permitted own profile fields | Not run |
| MAN-14 | Profile validation | Invalid future DOB, malformed email, and invalid field values are rejected | Not run |
| MAN-15 | Reports and low attendance | Values match source records and configured threshold | Not run |
| MAN-16 | Demo data command | Seed command creates/reuses expected synthetic records without resetting existing passwords | Not run |
| MAN-17 | Static files/theme | CSS and theme toggle render correctly after hard refresh | Not run |
| MAN-18 | Performance | Page and calculation timings measured on documented dataset/environment | Not run |

## 5. Defect log

| Defect | Description | Status |
|---|---|---|
| PROF-TEST-01 | Student profile test raised `KeyError: 'joining_year'` because form initializer referenced a model field not included in the form | Corrected file supplied; retest result pending |

Add further defects with a reproducible description, severity, linked requirement/test, owner, fix commit, and retest evidence.

## 6. Performance evidence

The team previously measured password verification at approximately 0.8675 seconds for one local check. This is a single measurement, not a full login-response benchmark. Do not use it as proof that the NFR is met or failed.

For the performance requirement, record:
- Machine/CPU/RAM and OS.
- Python/Django version and database.
- Dataset size (students, faculty, subjects, attendance rows).
- Warm-up procedure and number of repeated measurements.
- Median and maximum timings for login, dashboards, reports, and attendance percentage calculation.
- The exact performance acceptance thresholds from the approved SRS.

## 7. Sign-off

| Role | Name | Date | Signature / approval |
|---|---|---|---|
| Developer | To be completed | — | Pending |
| Reviewer | To be completed | — | Pending |
| Test owner | To be completed | — | Pending |
| Project supervisor (if required) | To be completed | — | Pending |

**Current conclusion:** the profile-specific test suite had one reported error in its first shared execution. A correction was supplied, but no post-correction test output or final full-suite/CI evidence has been supplied. The project is not documented as test-complete until those results are recorded.
