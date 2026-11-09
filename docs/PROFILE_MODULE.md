# SAMS Profile Module

## 1. Purpose and route

The Profile module provides a self-service profile page at `/profile/`. The page selects the profile associated with the currently authenticated user; the route does not accept a profile ID to select another person's profile.

## 2. Role-specific information

### Student
- Master-data identity: name, USN, section, semester, contact number.
- Linked account: email and username.
- Student profile: date of birth, derived age, joining year, CGPA, SGPA, address, parent/guardian name, relationship, email, and contact number.

The self-service form permits personal/contact/guardian updates. It does not expose USN, section, semester, joining year, CGPA, or SGPA as editable fields.

### Faculty
- Master-data identity: name, employee ID, department, contact number.
- Linked account: institutional email and username.
- Faculty profile: date of birth, derived age, date of joining, designation, personal email, and address.
- Teaching assignments: assigned subject-section combinations.

The self-service form permits personal/contact updates. Employee ID, department, designation, date of joining, and assignments are not editable through the faculty self-service form.

### Administrator
- Linked account: username and email.
- Admin profile: date of birth, derived age, date of joining, designation, contact number, and address.

## 3. Data model

- `StudentProfile` is one-to-one with `masterdata.Student`.
- `FacultyProfile` is one-to-one with `masterdata.Faculty`.
- `AdminProfile` is one-to-one with the configured custom user model.
- Age is calculated from DOB and is not stored.
- CGPA and SGPA are decimal fields validated between 0 and 10.

## 4. Profile lifecycle

The profile view uses `get_or_create` for the authenticated user's associated profile. Existing accounts can therefore open a profile without a separate bulk migration to create profile rows. Demo student and faculty profile values are populated by the demo seed command.

## 5. Administration and privacy

Profile models are registered in Django Admin for authorized institutional maintenance. Self-service profile access is scoped to `request.user`. Academic identifiers and academic scores are not editable through student self-service forms. Faculty employment identifiers and assignment data are not editable through faculty self-service forms.

Parent/guardian information is personal data. Use synthetic values in demonstrations and restrict access to authorized personnel.

## 6. Migrations and commands

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py test profiles
```

## 7. Tests

`profiles/tests.py` contains coverage for:
- Student sees own profile and academic data.
- Faculty profile displays teaching profile information.
- Administrator profile is created on first visit.
- Student cannot access another user's profile by an ID-style URL.

The first profile test run shared by the developer reported 3 passing tests and one `KeyError: 'joining_year'`. A corrected `profiles/forms.py` was supplied; the retest result must be recorded in `TEST_REPORT.md`.
