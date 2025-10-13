from django.core.management.base import BaseCommand
from tasks.models import Task
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Send email reminders for pending tasks'

    def handle(self, *args, **kwargs):
        pending_tasks = Task.objects.filter(status='pending')
        for task in pending_tasks:
            user_email = task.assigned_to.email
            if user_email:
                send_mail(
                    subject=f"Reminder: {task.title}",
                    message=f"Task '{task.title}' is still pending. Please review it.",
                    from_email='noreply@schoolmanager.com',
                    recipient_list=[user_email],
                )
        self.stdout.write(self.style.SUCCESS('Reminders sent successfully.'))
