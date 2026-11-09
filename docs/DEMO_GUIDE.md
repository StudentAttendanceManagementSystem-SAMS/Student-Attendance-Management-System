# SAMS Demonstration Guide

## 1. Demonstration preparation

Use a disposable local database and synthetic records.

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Before demonstrating attendance marking, sign in as Administrator and configure both active-term dates in Attendance Settings. The selected attendance date must fall inside the inclusive term range.

## 2. Demo accounts

| Role | Username | Default password |
|---|---|---|
| Administrator | Created locally with `createsuperuser` | The password selected during creation |
| Faculty | `DEMO-FAC-001` | `SamsDemo@123` |
| Student | `DEMO24CS001` | `SamsDemo@123` |

Additional generated accounts:
- Faculty: `DEMO-FAC-001` through `DEMO-FAC-040`.
- Students: `DEMO24CS001` through `DEMO24CS150`.

The seed command does not reset passwords for accounts that already exist. If a demo password is unknown, reset it through an authorized local administrative process; do not assume rerunning the seed command changes it.

## 3. Suggested walkthrough

### Part A — Administrator

1. Sign in with the locally created Administrator account.
2. Show the dashboard and institution summary.
3. Open master-data pages and show eight semester sections, students, faculty, subjects, and assignments.
4. Open Attendance Settings and show threshold, correction window, and configured term.
5. Open section-wise, subject-wise, and low-attendance reports.
6. Open My Profile and show the Administrator profile fields.
7. Sign out.

### Part B — Faculty

1. Sign in as `DEMO-FAC-001`.
2. Show the Faculty dashboard and assigned classes.
3. Open an assigned subject-section.
4. Show the roster and mark or review attendance for a date inside the active term.
5. Reopen a saved date to demonstrate existing statuses and correction-window behavior.
6. Open subject report/low-attendance views available to Faculty.
7. Open My Profile and show personal, employment, contact, and teaching-assignment details.
8. Attempt an unauthorized administrator route only as a controlled access-control test; expected result is denial/redirect, not data exposure.
9. Sign out.

### Part C — Student

1. Sign in as `DEMO24CS001`.
2. Show the Student dashboard and personal attendance summary.
3. Open subject-wise attendance and attendance history.
4. Open My Profile and show personal, academic, and parent/guardian details.
5. Demonstrate that academic identifiers and scores are not editable in the student self-service form.
6. Attempt to access another student's data only as a controlled privacy test; expected result is denial/404/redirect according to the route.
7. Sign out.

## 4. Demonstration tips

- Use synthetic demo data only. The generated names, email addresses, phone numbers, and addresses are fictional.
- Keep the active academic-term range configured before the Faculty attendance demonstration.
- The seed data includes deliberately lower attendance for some demo students so the low-attendance report can be demonstrated.
- The seed command creates/reuses demo users and records. It does not reset existing passwords.
- Do not display real passwords in a public recording or presentation. The default demo password is for a local disposable demonstration only.
- Capture screenshots only after verifying the displayed result in the running build.

## 5. Expected outcomes

| Demonstration | Expected result |
|---|---|
| Role login | User reaches the appropriate role experience. |
| Admin master data | Admin can manage permitted institutional records. |
| Faculty attendance | Faculty can access assigned classes and save valid attendance within the term. |
| Attendance correction | Existing session is reopened and edited within the correction window. |
| Reports | Aggregates reflect the underlying synthetic attendance records and configured scope. |
| Profile | Each role sees and edits only its permitted self-service details. |
| Privacy checks | A user cannot retrieve another user's private profile/attendance by changing a URL. |
| Logout | Session ends; protected pages require authentication on a fresh request. |
