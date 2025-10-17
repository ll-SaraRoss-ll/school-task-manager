#!/usr/bin/env bash
set -euo pipefail

# Load .env if present
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "Activating virtualenv if VENV_PATH set"
if [ -n "${VENV_PATH:-}" ] && [ -f "$VENV_PATH/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "$VENV_PATH/bin/activate"
fi

echo "Applying database migrations"
python manage.py migrate --noinput

echo "Collecting static files"
python manage.py collectstatic --no-input

echo "Registering scheduler (if using django-crontab)"
# Only run if django-crontab is used; skip harmlessly otherwise
if python - <<'PY' 2>/dev/null
import importlib,sys
try:
    importlib.import_module('django_crontab')
    print("yes")
except Exception:
    sys.exit(1)
PY
then
  python manage.py crontab add || echo "crontab add skipped or failed"
fi

echo "Restarting application server (example: systemctl or docker-compose)"
# Uncomment and adapt one of these to your environment:
# systemctl restart gunicorn
# docker compose up -d --build

echo "Deployment script completed"
