
from django.apps import AppConfig
import os
import logging

logger = logging.getLogger(__name__)

class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tasks"

    def ready(self):
        # Avoid running scheduler during migrations, collectstatic, tests, or when running management commands like makemigrations
        run_scheduler = os.environ.get("RUN_SCHEDULER", "True") == "True"
        is_manage_cmd = any(cmd in os.sys.argv for cmd in ("makemigrations", "migrate", "collectstatic", "shell", "test"))
        if run_scheduler and not is_manage_cmd:
            try:
                # Import here to avoid AppRegistryNotReady issues
                from .apscheduler import start
                start()
            except Exception as e:
                logger.exception("Failed to start APScheduler: %s", e)
        else:
            logger.info("Scheduler not started (RUN_SCHEDULER=%s, manage_cmd=%s)", run_scheduler, is_manage_cmd)
