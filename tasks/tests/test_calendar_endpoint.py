from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

from ..models import TimelineEntry, Activity

class CalendarEndpointTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        base_activity = Activity.objects.create(title='A', status=Activity.STATUS_CHOICES[0][0])

        # create timeline entries on different dates
        now = timezone.now()
        dates = [now, now + timedelta(days=1), now + timedelta(days=2)]
        for d in dates:
            TimelineEntry.objects.create(
                activity=base_activity,
                old_status=Activity.STATUS_CHOICES[0][0],
                new_status=Activity.STATUS_CHOICES[0][0],
                changed_at=d
            )

    def test_calendar_returns_grouped_dates(self):
        url = reverse('calendar')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # ensure keys are ISO date strings for today and next two days
        expected_keys = sorted([(timezone.localtime().date() + timedelta(days=i)).isoformat() for i in range(3)])
        returned_keys = sorted(data.keys())
        for k in expected_keys:
            self.assertIn(k, returned_keys)
            self.assertTrue(len(data[k]) >= 1)
