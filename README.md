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

More features and documentation coming soon...