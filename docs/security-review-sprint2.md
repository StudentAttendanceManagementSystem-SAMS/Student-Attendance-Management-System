# Sprint 2 Security Review

## Scope

- Server-side role checks
- Faculty assignment ownership
- Student record isolation
- CSRF protection on state-changing requests
- ORM-only data access
- No credentials or real student data in Git

## Commands Executed

1. **ORM and raw SQL search**

   `grep -RInE "cursor\(|\.raw\(|RawSQL|extra\(" accounts attendance analytics dashboard masterdata`

   Result: No matching patterns found.

2. **CSRF and unsafe HTML search**

   `grep -RInE "csrf_exempt|mark_safe|safe\}\}" accounts attendance analytics dashboard masterdata templates`

   Result: No matching patterns found.

3. **Python syntax verification**

   `python -m py_compile accounts/tests.py masterdata/tests.py`

   Result: Passed.

4. **Git whitespace verification**

   `git diff --check`

   Result: Passed.

## Security Regression Tests Added

| Test | Coverage |
|---|---|
| Faculty role boundary | Faculty cannot access administrator student management |
| Student role boundary | Student cannot access administrator student management |
| Administrator role boundary | Administrator can access student management |
| CSRF regression | Login POST without a CSRF token should be rejected |

## Findings

| Finding | Result |
|---|---|
| Raw SQL patterns | No matches found |
| CSRF exemptions | No matches found |
| Explicit unsafe HTML rendering patterns | No matches found |
| Role-based access coverage | Regression tests added |
| CSRF protection coverage | Regression test added |

## Review Status

- Reviewer: Pranav Somashekar
- Commit: Pending
- Date: 2026-11-03
- Status: In progress