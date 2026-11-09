# SAMS Installation and Local Setup Guide

## 1. Requirements

- Python 3.10+ (the team development environment used Python 3.12).
- `pip` and Git.
- Linux, macOS, or Windows.
- No separate database server is required for the default SQLite configuration.

## 2. Clone and create an environment

```bash
git clone https://github.com/StudentAttendanceManagementSystem-SAMS/Student-Attendance-Management-System.git
cd Student-Attendance-Management-System
python3 -m venv venv
source venv/bin/activate
```

Windows PowerShell activation:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The checked-in requirements file pins Django and its required supporting packages. Use the project's virtual environment for all management commands.

## 4. Configure and migrate

The default configuration uses SQLite at `BASE_DIR / "db.sqlite3"`.

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
```

If `makemigrations --check --dry-run` reports model changes, inspect them before creating or applying new migrations. Do not delete or rewrite existing migration files to silence the check.

## 5. Create an administrator

```bash
python manage.py createsuperuser
```

Use the credentials created by this command to sign in. The custom user manager assigns Django superusers the SAMS Administrator role.

## 6. Create synthetic demo data (optional)

```bash
python manage.py seed_demo
```

Default student/faculty password is `SamsDemo@123`. A different password for newly created demo accounts can be supplied:

```bash
python manage.py seed_demo --password 'YourStrongPassword'
```

See `DEMO_DATA.md` for record counts and account naming. The command is intended for a disposable/demo database, not production data.

## 7. Configure the academic term

After signing in as Administrator:

1. Open Attendance Settings.
2. Set the minimum attendance percentage and correction window as required.
3. Enter both active-term dates.
4. Save the configuration.

Attendance marking is blocked until both dates are configured. The configured range is inclusive.

## 8. Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

Stop the server with `Ctrl+C`.

## 9. Static files

For local development, `runserver` serves static files when `DEBUG=True` and the staticfiles app is enabled. For collection/deployment:

```bash
python manage.py collectstatic --noinput
```

The project must define a filesystem `STATIC_ROOT` (currently configured as `BASE_DIR / "staticfiles"`). Do not commit collected `staticfiles/` output unless the repository's deployment policy explicitly requires it.

## 10. Test commands

```bash
python manage.py check
python manage.py test
python manage.py test profiles
```

Run the full suite before integration or release. Capture the actual output and update `TEST_REPORT.md`; do not infer success from a test file existing.

## 11. Backup and reset guidance

Before applying changes to an existing local database, stop the server and copy `db.sqlite3` to a safe backup location. Do not delete the database as a routine troubleshooting step: it contains user accounts, attendance, and master data.

For a disposable demo reset only, create a separate copy or fresh checkout/database and rerun migrations and `seed_demo`. Never reset a database containing records that must be retained.

## 12. Troubleshooting commands

```bash
python --version
python -m django --version
python manage.py check
python manage.py showmigrations
python manage.py migrate --plan
```

Include the complete traceback when reporting a failure. Redact passwords, secret keys, session cookies, and personal information.
