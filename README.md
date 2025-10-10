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