# SAMS User Guide

**System:** Student Attendance Management System (SAMS)  
**Audience:** Administrator, Faculty, Student, and test personnel  
**Application URL (local):** `http://127.0.0.1:8000/`

## 1. Purpose

SAMS supports institutional master-data maintenance, attendance marking and correction, attendance calculation, reports, low-attendance monitoring, role-specific dashboards, and user profiles. Each user should sign in using the account and role assigned to them.

## 2. Sign in and sign out

1. Start the application using `docs/INSTALLATION.md`.
2. Open the application URL.
3. Enter the assigned username and password.
4. Confirm that the dashboard and navigation match the account role.
5. Use **Sign out** when finished, particularly on a shared device.

After sign-out, protected pages should require authentication again. Browser history may retain a history entry, but protected responses are configured not to be cached. If a protected page appears stale, refresh it; it must not expose protected content from an active session.

Repeated failed-login attempts produce a warning according to the configured session behavior. The warning is not an account lockout.

## 3. Administrator guide

### 3.1 Master data setup

Create records in dependency order:

1. Create Sections (semester 1–8).
2. Create Subjects (semester 1–8).
3. Create Students and assign each to the correct section.
4. Create Faculty.
5. Map subjects to sections.
6. Assign faculty to subject-section combinations.

Use unique identifiers: student USN, faculty employee ID, section name, and subject code. Review validation errors and confirm each saved record in its list page.

### 3.2 Attendance settings

1. Open **Attendance Settings**.
2. Set the minimum attendance threshold (default 75%).
3. Set the correction window in days (default 7).
4. Enter both active-term start and end dates.
5. Ensure the end date is not earlier than the start date.
6. Save and revisit the page to confirm persistence.

The term is institution-wide. Both dates are required before faculty can mark attendance. The allowed term range is inclusive. The correction window applies to edits of saved attendance; it does not override the term restriction.

### 3.3 Reports and monitoring

- Review section-wise and subject-wise attendance reports.
- Review below-threshold students against the configured threshold.
- Use date filters where offered and verify the selected scope.
- Treat a missing percentage as unavailable when there are no attendance records, rather than assuming it is zero.

### 3.4 Administrator profile

Open **My Profile** from the application navigation. The profile displays administrator account details and the available personal/employment/contact information. Permitted fields can be updated through the profile form. Authorized profile records are also registered in Django Admin.

## 4. Faculty guide

### 4.1 Dashboard and assigned classes

Sign in with a Faculty account. The dashboard and attendance selection should show only the subject-section combinations assigned to that faculty member. If no classes appear, ask the administrator to verify Faculty Assignments.

### 4.2 Mark attendance

1. Open **Mark Attendance**.
2. Select an assigned subject-section and a date.
3. Confirm the subject, section, and date shown on the page.
4. Mark each student Present or Absent.
5. Submit and review the confirmation/saved roster.

Attendance marking is rejected until the active term has been configured and for dates outside its inclusive range.

### 4.3 Correct attendance

1. Reopen the same subject-section and date.
2. Confirm previously saved statuses are loaded.
3. Change only the required statuses.
4. Submit and verify the result.

Existing attendance is editable only within the configured correction window. The default is seven days; the exact boundary behavior is documented in the RTM. The unique student/subject/date constraint prevents duplicate daily records.

### 4.4 Reports and low attendance

Use the Faculty report and low-attendance pages available in the navigation. Data should be restricted to the faculty member's assigned subject-section scope.

### 4.5 Faculty profile

Open **My Profile**. The page displays faculty identity, department, employment information, institutional/personal email, contact information, address, and assigned teaching combinations where available. The self-service form allows permitted personal/contact fields to be updated. Employee ID, department, designation, joining date, and assignments are not editable through the faculty self-service form.

## 5. Student guide

### 5.1 Dashboard and attendance

Sign in using the Student account. Review:
- Overall attendance percentage.
- Subject-wise attendance.
- Subjects below the configured threshold.
- Attendance history/report links available to the student.

A student should only see their own attendance information. If a record appears incorrect, contact the relevant faculty member or administrator; students do not mark or correct attendance.

### 5.2 Student profile

Open **My Profile**. The profile may display:
- Name, USN, email, and contact number.
- Date of birth and calculated age.
- Joining year, semester, and section.
- Current CGPA and SGPA.
- Address and parent/guardian details.

The self-service form allows permitted personal/contact and guardian details to be updated. Students cannot change their USN, section, semester, joining year, CGPA, or SGPA through their own profile. Academic/master-data values are maintained by authorized institutional staff.

## 6. Attendance calculations

- The default minimum attendance threshold is 75%.
- A percentage strictly below the threshold is considered below threshold; a value equal to the threshold is not below it.
- Overall attendance is a weighted aggregate of recorded classes, not a simple average of subject percentages.
- Percentages are rounded to two decimal places.
- Where no attendance records exist, the percentage is unavailable rather than automatically zero.
- Reports are scoped to the active academic term by default, with narrower date filters where provided.

## 7. Troubleshooting

| Symptom | Checks |
|---|---|
| Login rejected | Check username/password and account role; ask the administrator to verify the account. |
| User lands on the wrong page | Sign out, sign in again, and verify the role assigned to the account. |
| Access denied | Verify the role and, for Faculty, the subject-section assignment. |
| Faculty sees no classes | Ask the administrator to create the faculty assignment. |
| Attendance cannot be marked | Confirm the active term start/end dates are configured and the selected date is within the term. |
| Existing attendance is read-only | Check whether the correction window has expired. |
| Student profile is incomplete | Authorized staff should maintain academic/master-data fields; the student can update only permitted self-service fields. |
| Percentage is unavailable | Check whether attendance records exist for the relevant period and subject. |
| Static styles do not update | Hard-refresh the browser; for collected deployment assets, run `collectstatic` after confirming `STATIC_ROOT`. |
| Browser Back shows a protected page | Refresh the page; the server must redirect unauthenticated requests to login. Do not treat browser history as proof of an active session. |
| Migration/system-check error | Run `python manage.py check`, `python manage.py showmigrations`, and inspect the full terminal traceback. |

## 8. Privacy and security

- Use synthetic demo data for demonstrations and testing.
- Do not share passwords or use another person's account.
- Do not attempt to access another user's profile or attendance by changing URLs.
- Do not commit real student or parent contact details to source control.
- Report suspected access-control defects with role, route, reproduction steps, and redacted evidence.

## 9. Defect reporting

Include the account role, page/action, synthetic record identifiers, steps to reproduce, expected result, actual result, timestamp, and relevant terminal/browser output. Remove passwords, session cookies, and personal data from screenshots and logs.
