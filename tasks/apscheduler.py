# tasks/apscheduler.py
import logging
from django.conf import settings
from django.core.management import call_command
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

def send_reminders_job():
    logger.info("Running send_task_reminders job")
    try:
        call_command("send_task_reminders")
    except Exception as e:
        logger.exception("send_task_reminders failed: %s", e)

def start():
    """
    Start the APScheduler scheduler and register the daily job.
    This should be called from AppConfig.ready() of the tasks app.
    """
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Job id used to avoid duplicate jobs
    job_id = "send_task_reminders_daily"

    # CronTrigger: run daily at 08:00 (server time / TIME_ZONE)
    trigger = CronTrigger(hour=8, minute=0)

    # If job with same id exists, remove it first to avoid duplicates
    existing = scheduler.get_jobs()
    if any(j.id == job_id for j in existing):
        logger.info("Job %s already registered with scheduler (skipping add)", job_id)
    else:
        scheduler.add_job(
            send_reminders_job,
            trigger,
            id=job_id,
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
        )
        logger.info("Added job %s to scheduler", job_id)

    scheduler.start()
    logger.info("APScheduler started")
