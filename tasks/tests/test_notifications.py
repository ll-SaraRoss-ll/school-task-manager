from django.test import TestCase, override_settings
from django.core import mail
from django.core.management import call_command
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from django.conf import settings
from tasks.models import Activity

User = get_user_model()

@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
                   REMINDER_WINDOW_DAYS=1)
class ReminderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="pass")
        self.activity = Activity.objects.create(
            title="Test Activity",
            assigned_to=self.user,
            status="pending",
            next_due_date=date.today() + timedelta(days=1),
        )

    def test_send_task_reminders_sends_emails(self):
        mail.outbox = []
        call_command("send_task_reminders")
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertIn("Test Activity", message.subject)
        # plain text body
        self.assertIn("Test Activity", message.body)
        # html alternative
        alternatives = message.alternatives
        self.assertTrue(any("Test Activity" in alt[0] for alt in alternatives))
