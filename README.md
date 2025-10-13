# School Task Manager: 
A lightweight backend for managing school tasks and activities. Built with Django and SQLite for solo or low-traffic use.

# Setup Instructions
1. Clone the repo
bash
git clone https://github.com/ll-SaraRoss-ll/school-task-manager.git
cd school-task-manager

2. Create and activate virtualenv
bash
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash

3. Install dependencies
bash
pip install django djangorestframework django-cors-headers django-crontab

4. Run migrations
bash
python manage.py makemigrations
python manage.py migrate

5. Start development server
bash
python manage.py runserver

# Testing
bash
python manage.py test

# Notes
Database: SQLite (db.sqlite3)

API: Django REST Framework

Cron jobs: Email reminders via django-crontab


## Key implementation details
Models

TaskTable: title, description, timeline, assigned_to (FK to user), resources_budget (JSON), performance_indicators, status, created_at, updated_at.

Activity: task_table (FK to TaskTable; temporarily nullable during migration), title, description, timeline, assigned_to, resources_budget, performance_indicators, status, next_due_date, created_at, updated_at.

Activity.save() calculates and sets next_due_date for recurring timelines using utils functions.

Migrations

Reviewed and reconciled tasks/migrations/0001_initial.py and 0002_initial.py.

Added explicit rename operations or temporary-null migrations to avoid interactive makemigrations prompts.

Backfilled missing FK and title values in the DB before making fields non-nullable.

API behavior

TaskTable creation is performed server-side with assigned_to set to the authenticated user.

TaskTableSerializer exposes assigned_to as read-only so clients cannot spoof ownership.

Viewsets use DRF permissions; authenticated access is required for writes.

Public API endpoints (development)
All endpoints are mounted under /api/tasks/ (adjust if your project-level urls.py mounts differently).

List TaskTables

GET /api/tasks/tables/

Create TaskTable

POST /api/tasks/tables/

Required fields: title (string), timeline (one of: one-off, yearly, quarterly, term) — assigned_to is set from the authenticated user

Retrieve / Update / Delete TaskTable

GET/PUT/DELETE /api/tasks/tables/{id}/

List Activities

GET /api/tasks/activities/

Create Activity

POST /api/tasks/activities/

Provide task_table (id), title, timeline, etc. next_due_date is auto-calculated for recurring timelines

Retrieve / Update / Delete Activity

GET/PUT/DELETE /api/tasks/activities/{id}/

Authentication: use Django session login (browsable API) or basic/token auth for development. The browsable API login is available at /api-auth/login/.

How to run locally (quick)
Create and activate your virtualenv, install requirements.

Apply migrations:

python manage.py makemigrations

python manage.py migrate

Create a superuser if needed:

python manage.py createsuperuser

Start dev server:

python manage.py runserver

Use the browsable API or curl to interact with endpoints (include authentication for write operations).

## Features / Audit & Calendar
TimelineEntry purpose and fields TimelineEntry records every status transition for an Activity to provide an auditable history trail. Fields: activity (FK to Activity), old_status (previous status), new_status (current status), changed_at (timestamp recorded on create), metadata (optional JSON blob for user id, IP, reason, request id).

How signals log status changes and attach metadata A pre_save signal on Activity compares the instance’s status against the stored DB value and creates a TimelineEntry when the status changes. To include contextual metadata (for example, the acting user or request info), attach a dict to the Activity instance before saving:

py
instance._status_change_metadata = {'user_id': request.user.id, 'note': 'approved via UI'}
instance.status = 'in_progress'
instance.save()
The signal reads instance._status_change_metadata and stores it in TimelineEntry.metadata..

Calendar endpoint behavior and JSON shape The calendar endpoint returns upcoming timeline entries grouped by ISO date strings (YYYY-MM-DD) suitable for calendar UIs. Route: /api/tasks/calendar/. Response shape:

json
{
  "2025-10-13": [
    {"id": 1, "activity": 3, "old_status": "todo", "new_status": "in_progress", "changed_at": "2025-10-13T11:21:00Z"}
  ],
  "2025-10-14": [
    {"id": 2, "activity": 4, "old_status": "in_progress", "new_status": "done", "changed_at": "2025-10-14T08:00:00Z"}
  ]
}
Entries are keyed by the date portion of changed_at; each value is an array of TimelineEntry objects with the fields id, activity, old_status, new_status, changed_at.

Configuration and checks
Confirm AppConfig usage in settings Ensure INSTALLED_APPS contains the Tasks AppConfig:

py
INSTALLED_APPS = [
  # ...
  'tasks.apps.TasksConfig',
  # ...
]
Lint, tests, and CI commands Run linting and tests locally before committing:

Lint:

bash
flake8 tasks
# or
pylint tasks
Run tests:

bash
python manage.py test
Suggested git workflow and commit messages Stage, commit, and push the changes with clear messages:

bash
git add tasks/ README.md
git commit -m "Add TimelineEntry model and logging signals"
git add tasks/ README.md
git commit -m "Implement /api/calendar/ endpoint and tests"
git push origin your-branch-name
Replace your-branch-name with the branch you are using.

Developer notes (short)
Ensure tasks/apps.TasksConfig.ready() imports tasks.signals to wire receivers.

Use select_related('activity') or values() in the calendar view for performance when serializing many entries.

Keep TimelineEntry.STATUS_CHOICES stable and shared with Activity via a single constant to avoid import-order issues.