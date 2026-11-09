# Testing Strategy, Coverage, and GitHub Actions

## 1. Four-person responsibility split

Use the following split as a proposed team allocation. Replace Member 1–4 with actual names and Jira owners.

| Owner | Responsibility | Test level / evidence | Suggested GitHub Actions job |
|---|---|---|---|
| Member 1 | Unit tests for models, forms, validators, permissions, and calculation services | Unit tests; Django test output; unit test cases | `unit-tests` |
| Member 2 | Integration tests across attendance, persistence, and analytics | Integration tests; database assertions; service output | `integration-tests` |
| Member 3 | System tests across real login, role dashboards, authorization, logout, and profile journeys | System tests using Django test client; manual browser evidence | `system-tests` |
| Member 4 | CI workflow, coverage/branch coverage, test report, and pipeline maintenance | GitHub Actions runs; coverage XML/HTML artifacts; CI gate | `coverage`, `ci-gate` |

All four members should review one another's tests. This is division of ownership, not permission for each member to test only their own code.

## 2. What the four test types mean

### Unit testing
Tests one small unit in isolation: a function, model rule, validator, permission helper, or calculation. Examples in SAMS include percentage calculations, invalid role rejection, semester constraints, and form validation.

### Integration testing
Tests that multiple components work together. The supplied attendance integration tests call the Faculty attendance view, write/read SQLite records, and verify that the analytics service sees the saved attendance. They also check assignment authorization and update-not-duplicate behavior.

### System testing
Tests the application as a user-facing system. The supplied system tests authenticate Admin, Faculty, and Student through the login endpoint, load the role dashboard, log out, and verify that a protected page redirects after logout. Add browser/manual evidence for visual behavior and real navigation.

### CI/CD
Continuous Integration (CI) automatically installs dependencies and runs checks/tests/coverage on pushes and pull requests. Continuous Delivery/Deployment (CD) additionally packages or deploys a verified build to a target environment. This repository has a CI workflow; it does not have a deployment target or deployment credentials configured, so do not claim automated deployment is implemented. Add a CD job only after the team chooses a host and configures protected GitHub Environment secrets.

## 3. Install coverage.py

```bash
pip install coverage
```

The supplied `.coveragerc` enables branch measurement and scopes the report to SAMS application packages. Test files, migrations, Django project configuration, and admin/app registration boilerplate are omitted from the coverage denominator.

## 4. Generate code and branch coverage locally

Run from the project root with the virtual environment activated:

```bash
coverage erase
coverage run --rcfile=.coveragerc --branch manage.py test
coverage report --rcfile=.coveragerc --show-missing
coverage html --rcfile=.coveragerc
coverage xml --rcfile=.coveragerc -o coverage.xml
```

Open the detailed HTML report:

```bash
xdg-open htmlcov/index.html
```

The terminal summary reports statement coverage. Because branch measurement is enabled, it also reports branches and partial branches; the percentage shown in the report is the combined coverage percentage (statements plus branch opportunities). Use the HTML report to inspect missing lines and untested branch paths.

To see a concise machine-readable XML output, use `coverage.xml`. Do not confuse line/statement coverage with branch coverage: a line can execute while one of its `if/else` paths remains untested.

## 5. GitHub Actions evidence

The workflow `.github/workflows/django-tests.yml` runs:
1. Unit tests.
2. Integration tests.
3. System tests.
4. Full-suite coverage with branch measurement.
5. A final CI gate that fails if any required job fails.

On a push or pull request to `develop`, open the repository's **Actions** tab and select the `SAMS Quality Checks` run. Show the individual job results. Download the `sams-coverage-report` artifact to present `htmlcov/index.html` and `coverage.xml`.

The CI workflow uses an ephemeral SQLite test database created by Django's test runner. It does not use the developer's local `db.sqlite3`.

## 6. Local commands matching CI

```bash
# Unit tests
python manage.py test accounts masterdata analytics

# Integration tests
python manage.py test attendance.test_integration

# System tests
python manage.py test dashboard.test_system profiles

# All tests
python manage.py test

# Coverage including branch paths
coverage erase
coverage run --rcfile=.coveragerc --branch manage.py test
coverage report --rcfile=.coveragerc --show-missing
coverage html --rcfile=.coveragerc
```

## 7. How to present results

For each run, record:
- Git commit SHA and branch.
- Date/time and Python/Django versions.
- Test level and exact command/workflow job.
- Number of tests, passed, failed, errors, skipped.
- Statement coverage percentage.
- Branch coverage percentage (from the HTML/XML report; record the actual reported value).
- Links to GitHub Actions run and uploaded artifact.
- Defect IDs and retest evidence.

Do not invent a target percentage or report a value before running the suite. Agree a threshold with the supervisor/team. Once a reliable baseline exists, a coverage gate can be added (for example, `coverage report --fail-under=...`), but do not choose an arbitrary gate that makes the current project fail without an agreed rationale.

## 8. Important limitation: CI is not automatically CD

The supplied GitHub Actions workflow is a continuous-integration pipeline. It verifies code on pushes and pull requests. It does not deploy SAMS because no hosting provider, deployment process, environment, or secrets were specified. For an academic demo, a successful CI pipeline plus a documented manual deployment/demo process may be sufficient if that matches the rubric. If the rubric explicitly requires CD, select a deployment target first and add a separate protected deployment workflow.

## 9. Evidence checklist

- [ ] Each team member's name and ownership added to the allocation table.
- [ ] Unit test job passes.
- [ ] Integration test job passes.
- [ ] System test job passes.
- [ ] Coverage job passes and uploads HTML/XML artifact.
- [ ] Actual statement and branch coverage values recorded.
- [ ] CI gate passes for the final pull request.
- [ ] Manual browser test screenshots/logs are captured with synthetic data only.
- [ ] Final commit SHA and Actions URL added to `TEST_REPORT.md`.
