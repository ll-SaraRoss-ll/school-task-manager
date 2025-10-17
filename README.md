School Task Manager
A lightweight Django REST backend for managing school tasks and activities. Built for solo or low-traffic use with SQLite locally and PostgreSQL recommended for production. Includes activity reminders, timeline auditing, calendar feed, role-based permissions, and OpenAPI docs.

Quick start (run locally)
Clone

bash
git clone https://github.com/ll-SaraRoss-ll/school-task-manager.git
cd school-task-manager
Create and activate virtualenv

bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows Git Bash
source venv/Scripts/activate
Install dependencies

bash
pip install -r requirements.txt
Create .env (project root) — example values

Code
DJANGO_SECRET_KEY=replace-with-a-secret
DJANGO_DEBUG=True
DJANGO_ENV=development
DJANGO_TIME_ZONE=Africa/Addis_Ababa
REMINDER_WINDOW_DAYS=1
RUN_SCHEDULER=False

# DB (for production use a proper DATABASE_URL or Postgres)
POSTGRES_DB=school_task_manager
POSTGRES_USER=db_user
POSTGRES_PASSWORD=db_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Email (SendGrid example). For local dev use locmem backend instead.
SENDGRID_API_KEY=SG.xxxxx
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
SERVER_EMAIL=server@yourdomain.com

# Optional for deploy.sh
VENV_PATH=/absolute/path/to/venv
Add .env to .gitignore:

Code
.env
Apply database migrations

bash
python manage.py makemigrations
python manage.py migrate
Create a superuser (optional)

bash
python manage.py createsuperuser
Run the development server

bash
python manage.py runserver
Visit the API

Browsable API root or DRF endpoints, e.g. http://127.0.0.1:8000/api/tasks/

Swagger UI: http://127.0.0.1:8000/api/docs/

Schema JSON/YAML: http://127.0.0.1:8000/api/schema/

Environment and configuration
settings driven by environment variables in .env.

Key env variables: DJANGO_SECRET_KEY, DJANGO_DEBUG, TIME_ZONE, REMINDER_WINDOW_DAYS, RUN_SCHEDULER, SENDGRID_API_KEY, DEFAULT_FROM_EMAIL.

For local testing set:

DJANGO_DEBUG=True

EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend

TIME_ZONE should match your server timezone so scheduled jobs using TIME_ZONE run at the intended hour.

Scheduler (APScheduler)
We use django-apscheduler for cross-platform scheduling.

Enable scheduler in production by setting RUN_SCHEDULER=True.

The scheduled job runs the management command send_task_reminders daily at 08:00 server time (configurable by editing tasks/apscheduler.py CronTrigger).

To avoid multiple scheduler instances, only enable RUN_SCHEDULER on one process (or run a single dedicated scheduler worker).

Quick checks:

bash
# start server with scheduler enabled
RUN_SCHEDULER=True python manage.py runserver

# disable scheduler during tests
RUN_SCHEDULER=False python manage.py test
Reminder emails
Templates: tasks/templates/tasks/reminder_email.txt and reminder_email.html.

Management command: python manage.py send_task_reminders

Uses REMINDER_WINDOW_DAYS to compute reminder date.

Queries activities with next_due_date == today + REMINDER_WINDOW_DAYS and status in pending/in-progress.

Sends plain-text + HTML to activity.assigned_to.email.

For provider integration use Anymail (Mailgun recommended) or the SendGrid SDK. For local testing use locmem or console backend.

Endpoints (high level)
All endpoints are mounted under the tasks API prefix (adjust if your project urls differ).

TaskTables

GET /api/tasks/tables/ — list

POST /api/tasks/tables/ — create (assigned_to set server-side)

GET/PUT/DELETE /api/tasks/tables/{id}/ — retrieve/update/delete

Activities

GET /api/tasks/activities/ — list

POST /api/tasks/activities/ — create (next_due_date auto-calculated for recurring timelines)

GET/PUT/DELETE /api/tasks/activities/{id}/

Calendar

GET /api/tasks/calendar/ — returns timeline entries grouped by date (YYYY-MM-DD) suitable for calendar UIs

Reports

GET /api/tasks/reports/overdue/

GET /api/tasks/reports/upcoming/?days=N

Docs

GET /api/schema/

GET /api/docs/

Authentication

Session auth (browsable API) and TokenAuthentication available for API use. Writes require authentication.

Models & behavior (concise)
TaskTable: title, description, timeline, assigned_to (FK), resources_budget (JSON), performance_indicators, status, timestamps.

Activity: FK to TaskTable, title, timeline, assigned_to, resources_budget, status, next_due_date, timestamps.

TimelineEntry: records status transitions (activity FK, old_status, new_status, changed_at, metadata JSON).

Activity.save() computes next_due_date for recurring timelines using utility functions.

Signals: Activity change signal creates TimelineEntry when status changes. Attach instance._status_change_metadata before save to include context.

Example to attach metadata before changing status:

py
instance._status_change_metadata = {'user_id': request.user.id, 'note': 'approved via UI'}
instance.status = 'in_progress'
instance.save()
Tests & QA
Run tests:

bash
# disable scheduler for tests
RUN_SCHEDULER=False python manage.py test
Notification tests:

Use django.core.mail.backends.locmem.EmailBackend or override settings in tests.

Assert len(mail.outbox) equals expected emails and check subject/body content and HTML alternative.

Manual QA checklist:

Create an activity due tomorrow → run send_task_reminders or wait for scheduler at 08:00, confirm email arrival.

Confirm no emails for tasks outside the reminder window.

Confirm calendar endpoint groups entries by date.

Confirm TimelineEntry records appear after status transitions, and metadata saved when provided.

Confirm API permissions (Owner vs Director groups).

Deployment (deploy.sh)
Place deploy.sh at project root (next to manage.py). Basic usage:

Make executable:

bash
chmod +x deploy.sh
Run it:

bash
./deploy.sh
What deploy.sh does

Loads .env if present

Optionally activates virtualenv if VENV_PATH is set

Runs python manage.py migrate

Runs python manage.py collectstatic --no-input

Attempts python manage.py crontab add only if django-crontab is installed (guarded)

Prints progress and exits non-zero on error

Notes for production

Use a proper secret storage instead of .env for production (hosting secret manager).

Use Postgres and set DATABASE_URL or DB_* env variables.

Run the scheduler in a single dedicated process or use a separate process for the scheduler.

Use gunicorn/uvicorn + systemd or container orchestration for production.

Docker (optional)

Use a docker-compose setup that runs migrations and collectstatic in the container start-up step; adapt deploy.sh accordingly.

Git workflow & release
Suggested workflow

bash
git checkout -b feature/notifications
git add .
git commit -m "Implement send_task_reminders and APScheduler integration"
git push origin feature/notifications
Tag release

bash
git tag -a v1.0.0 -m "Release: notifications & scheduling complete"
git push origin main
git push --tags
Troubleshooting (common issues)
ModuleNotFoundError: anymail — install pip install django-anymail or switch EMAIL_BACKEND to locmem/console for dev.

fcntl on Windows — django-crontab is Unix-only; use APScheduler (implemented) or Windows Task Scheduler.

Duplicate scheduled jobs — ensure RUN_SCHEDULER=True only on one process or use dedicated scheduler worker.

Emails not delivered — verify SENDGRID_API_KEY/MAILGUN credentials and DEFAULT_FROM_EMAIL.

Implementation notes for developers
Ensure tasks.apps.TasksConfig.ready() imports tasks.signals.

Use select_related for calendar and report endpoints to reduce DB hits.

Keep TimelineEntry.STATUS_CHOICES stable and shared across models.

Use REMINDER_WINDOW_DAYS env var to control reminder timing.