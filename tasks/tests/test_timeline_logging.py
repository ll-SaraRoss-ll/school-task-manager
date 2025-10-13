from django.test import TestCase
from .models import TimelineEntry, Activity

class TimelineLoggingTest(TestCase):
    def setUp(self):
        self.activity = Activity.objects.create(
            # fill required fields for Activity model; adapt field names as needed
            title='Test',
            status=Activity.STATUS_CHOICES[0][0]
        )

    def test_status_change_creates_timeline_entry(self):
        old_status = self.activity.status
        new_status = Activity.STATUS_CHOICES[1][0] if len(Activity.STATUS_CHOICES) > 1 else old_status

        # attach metadata to be captured by the signal
        self.activity._status_change_metadata = {'note': 'test change'}
        self.activity.status = new_status
        self.activity.save()

        entries = self.activity.timeline_entries.all()
        self.assertEqual(entries.count(), 1)
        entry = entries.first()
        self.assertEqual(entry.old_status, old_status)
        self.assertEqual(entry.new_status, new_status)
        self.assertEqual(entry.metadata.get('note'), 'test change')
