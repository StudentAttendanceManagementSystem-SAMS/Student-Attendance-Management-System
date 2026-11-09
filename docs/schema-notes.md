# Schema Notes

The relational schema uses Django models and foreign keys/one-to-one relationships. The design separates identity, institutional master data, attendance facts, configuration, and role-specific profile attributes.

- A student's section is reached through the Student-to-Section foreign key rather than duplicating section names.
- Student and Faculty institutional records are one-to-one with the custom User model.
- SubjectSection resolves the subject-to-section mapping.
- FacultyAssignment associates a faculty member with a subject and section.
- Attendance stores the student, subject, faculty member who marked it, date, status, and timestamps.
- A unique constraint prevents duplicate attendance for a student/subject/date.
- Profile models are one-to-one extensions of Student, Faculty, or User.
- Semester values are restricted to 1–8 for Section, Subject, and Student.
- Profile age is derived from date of birth and is not stored.

## Attendance configuration

`AttendanceConfig` is singleton-style (primary key 1) and stores:
- Minimum attendance threshold (default 75%).
- Correction window in days (default 7).
- Institution-wide active-term start and end dates.

The term dates are configured together. The end date cannot precede the start date. Faculty marking is blocked until the dates are configured and is allowed only within the inclusive date range. The term is institution-wide; section rows do not duplicate term dates.

See `DATABASE_SCHEMA.md` for the entity inventory and ER diagram.
