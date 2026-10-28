# SAMS User Guide

**System:** Student Attendance Management System (SAMS)
**Audience:** Administrators, Faculty, Students, and test personnel
**Status:** Operational guide based on the current repository. Exact labels may vary with the UI templates in the delivered build.

## 1. Purpose

SAMS provides role-specific access to student attendance, master data, attendance marking, attendance percentages, threshold configuration, and reports. Users should use only the account and role assigned to them.

## 2. Sign in and sign out

1. Start the Django application using the setup instructions in the root `README.md`.
2. Open `http://127.0.0.1:8000/`.
3. Enter your assigned username and password.
4. Confirm that the page/dashboard corresponds to your role.
5. Use the application's logout action when finished, especially on a shared computer.

If login fails, check the username/password and contact the system administrator. Do not share passwords. Protected pages should redirect unauthenticated users to login; after logout, protected pages should no longer be available through the old session.

## 3. Administrator guide

### 3.1 Configure institution master data

Set up data in a sensible order so that related records can be selected in forms:

1. Create sections and their academic details.
2. Create subjects and the applicable semester details.
3. Create student records and assign each student to the correct section.
4. Create faculty records.
5. Assign faculty to the appropriate subject/section combinations.
6. Verify that unique identifiers (such as student USN, faculty employee ID, section name, and subject code) are not duplicated.

Use the application's validation messages to correct invalid or duplicate data. Verify the saved record in the relevant list after creating or updating it.

### 3.2 Configure the attendance threshold

1. Sign in as an Administrator.
2. Open the attendance threshold/settings page through the application navigation.
3. Enter the required minimum attendance percentage (an integer from 0 to 100).
4. Submit/save the setting.
5. Reopen the page or refresh it and confirm the saved value persists.

The default configured threshold is 75%. The threshold is used by the low-attendance identification feature. Confirm the institution's approved policy before changing it.

### 3.3 Review reports

- **Section-wise report:** review attendance aggregates grouped by section.
- **Subject-wise report:** review attendance aggregates grouped by subject, including aggregation across sections where applicable.
- **Below-threshold report:** review students whose calculated attendance falls below the configured threshold.

Review the selected date/data scope and interpret a missing percentage carefully. If no attendance sessions have been recorded for a student/subject, a percentage may be unavailable rather than 0%.

Administrators should not use report output as a substitute for checking source attendance records when a discrepancy is reported.

## 4. Faculty guide

### 4.1 Open an assigned class

1. Sign in with a Faculty account.
2. Open the attendance/class selection page.
3. Select a subject/section assigned to your account.
4. Select the attendance date and open the roster.

Only assigned classes should be offered. If no assignments appear, contact the administrator to verify the faculty assignment.

### 4.2 Mark attendance

1. Check that the subject, section, and date are correct.
2. Review the complete roster.
3. Mark each student as **Present** or **Absent**.
4. Submit the attendance.
5. Verify the confirmation or saved roster.

The application treats an omitted/invalid status defensively according to its current server-side behavior; users should nevertheless select an explicit status for every student.

### 4.3 Correct an existing session

1. Reopen the same assigned subject/section and date.
2. Confirm the previously saved values are displayed.
3. Correct the necessary statuses.
4. Submit again and verify the saved values.

The data model prevents more than one attendance record for the same student, subject, and date. Re-submission is intended to update the existing record rather than create a duplicate. Do not create a second session for the same subject/date to correct a typo.

### 4.4 View low-attendance information

Use the low-attendance page available to your role. Faculty visibility is scoped to assigned sections in the current tests. If a student appears unexpectedly, verify the attendance records, configured threshold, and assignment scope.

## 5. Student guide

1. Sign in using the Student account.
2. Open the student dashboard/attendance area.
3. Review the attendance information and percentages displayed for your own account.
4. If a record looks incorrect, contact the faculty member or administrator responsible for the class; do not attempt to edit attendance as a student.

A student must not be able to access administrator report pages or view another student's private attendance through URL manipulation.

## 6. Attendance percentage and threshold interpretation

- Percentage is calculated from recorded attendance data by the application.
- The threshold defaults to 75% and can be changed by an authorized administrator.
- A student is considered below threshold when the calculated percentage is strictly less than the configured threshold; a value exactly equal to the threshold is not below it.
- Where no classes/attendance records are available, the percentage may be represented as unavailable. Do not interpret unavailable as 0% without checking the underlying records.

## 7. Troubleshooting

| Symptom | What to check |
|---|---|
| Cannot sign in | Credentials, account existence, and assigned role; ask the administrator for help. |
| Page redirects to login | Session may have expired or the page requires authentication. Sign in again. |
| Access denied | Confirm that your role is authorized for the page. Faculty should verify their assignments. |
| No classes shown to faculty | Ask the administrator to verify subject/section assignments. |
| Duplicate record or unexpected attendance | Reopen the same subject/section/date and verify saved statuses; report persistent discrepancies. |
| Percentage is blank/unavailable | Confirm that attendance sessions have been recorded for the relevant student and subject. |
| Student appears below threshold | Verify the configured threshold and source attendance records. |
| Server or migration error | Check terminal output, installed requirements, migrations, and Django system checks; report the error with the traceback to the maintainer. |

## 8. Security and data handling

- Do not share accounts or passwords.
- Use only the role assigned to you.
- Do not attempt to access other users' records by changing URLs or identifiers.
- Use synthetic or approved test data during testing.
- Do not commit real credentials, production data, or secrets to Git.
- Report suspected authorization failures or data discrepancies to the project maintainer.

## 9. Support and feedback

When reporting a defect, include the role used, page/action, test data identifiers (non-sensitive), expected result, actual result, reproduction steps, and a screenshot or log with secrets removed.
