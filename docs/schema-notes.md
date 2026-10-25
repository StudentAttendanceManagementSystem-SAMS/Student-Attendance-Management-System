# Schema notes

The schema follows SRS Appendix A and is in third normal form.

- Every non-key column depends only on its own table's key. A student's section name is not copied into the student row; it is reached through the section foreign key.
- The many-to-many relationships are resolved with SubjectSection (subject to section) and FacultyAssignment (faculty to subject to section).
- Unique constraints stop duplicate USNs, employee IDs, section names, subject codes, mappings, assignments and daily attendance rows.
- Moving from SQLite to another database needs no schema change because nothing depends on SQLite-specific features.
