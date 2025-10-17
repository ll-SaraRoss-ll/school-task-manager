from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from tasks.models import Activity

REMINDER_WINDOW_DAYS = int(getattr(settings, "REMINDER_WINDOW_DAYS", 1))

class Command(BaseCommand):
    help = "Send email reminders for activities due in reminder window"

    def handle(self, *args, **options):
        today = timezone.now().date()
        reminder_date = today + timedelta(days=REMINDER_WINDOW_DAYS)

        qs = Activity.objects.filter(
            next_due_date=reminder_date,
            status__in=["pending", "in-progress"]
        ).select_related("assigned_to")

        total = qs.count()
        self.stdout.write(f"Found {total} activities due on {reminder_date}")

        sent = 0
        failed = 0

        for activity in qs:
            user = activity.assigned_to
            if not user or not user.email:
                self.stderr.write(f"Skipping activity {activity.pk}: no assigned user email")
                failed += 1
                continue

            context = {"activity": activity, "user": user}
            subject = f"Reminder: {activity.title}"
            text_body = render_to_string("tasks/reminder_email.txt", context)
            html_body = render_to_string("tasks/reminder_email.html", context)

            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
                sent += 1
                self.stdout.write(f"Sent reminder to {user.email} for activity {activity.pk}")
            except Exception as e:
                failed += 1
                self.stderr.write(f"Failed to send to {user.email} for activity {activity.pk}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Reminders complete: sent={sent}, failed={failed}"))
