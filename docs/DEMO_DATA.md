# SAMS Demo Data

## 1. Generate data

From the repository root, after activating the virtual environment and applying migrations:

```bash
python manage.py migrate
python manage.py seed_demo
```

Optional password for newly created demo accounts:

```bash
python manage.py seed_demo --password 'YourStrongPassword'
```

The default password is `SamsDemo@123`.

## 2. Dataset

The command uses a fixed random seed for reproducible synthetic values and creates/reuses:

| Data | Quantity / pattern |
|---|---|
| Sections | 8, one per semester (1–8) |
| Students | 150 |
| Faculty | 40 |
| Subjects | 5 per semester section (40 total) |
| Subject-section mappings | One per generated subject/semester section |
| Faculty assignments | One generated faculty assignment per mapped subject-section |
| Attendance | Up to 20 recent weekdays per student/subject combination; existing unique rows are not duplicated |
| Student profiles | Created/updated for generated demo students |
| Faculty profiles | Created/updated for generated demo faculty |

Some demo students are generated with a lower attendance probability to make below-threshold demonstrations possible.

## 3. Account naming

| Role | Username range |
|---|---|
| Student | `DEMO24CS001`–`DEMO24CS150` |
| Faculty | `DEMO-FAC-001`–`DEMO-FAC-040` |
| Administrator | Create separately using `python manage.py createsuperuser` |

All generated student/faculty accounts created by the command use the supplied password. The command does not change passwords for accounts that already exist.

## 4. Idempotency and cautions

- The command is wrapped in a database transaction.
- It uses `get_or_create`, `update_or_create`, and conflict-ignoring attendance insertion for repeatable setup.
- Profile demo values are refreshed for generated student/faculty profile rows.
- Existing login passwords are not reset.
- Existing attendance rows are not overwritten by the seed insertion.
- The command does not delete records.
- Use only in a disposable/demo database; do not run against production student data without an approved data plan.

## 5. Profile demo values

Generated student profiles include synthetic DOB, joining year, CGPA/SGPA, address, and parent/guardian information. Generated faculty profiles include synthetic DOB, joining date, designation, personal email, and address. All generated names, emails, phone numbers and addresses are fictional demonstration data.
