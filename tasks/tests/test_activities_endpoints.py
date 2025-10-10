from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from tasks.models import TaskTable, Activity
from datetime import date
from tasks.utils import get_next_yearly_date

User = get_user_model()

class ActivityEndpointsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.table = TaskTable.objects.create(title='T1')

    def test_activity_crud_and_recurrence(self):
        url = reverse('activity-list')
        data = {
            'task_table': self.table.id,
            'title': 'Act1',
            'timeline': 'yearly',
        }
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, 201)
        act = Activity.objects.get(id=res.data['id'])
        expected_next = get_next_yearly_date(date.today())
        self.assertEqual(act.next_due_date, expected_next)
