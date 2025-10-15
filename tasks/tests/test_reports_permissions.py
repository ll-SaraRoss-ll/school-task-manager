from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.urls import reverse
from rest_framework.test import APIClient
from ..models import Activity, TaskTable  # adjust imports as needed

OWNER_GROUP = 'Owner'
DIRECTOR_GROUP = 'Director'

class ReportsPermissionsTests(TestCase):
    def setUp(self):
        # groups
        owner_group, _ = Group.objects.get_or_create(name=OWNER_GROUP)
        director_group, _ = Group.objects.get_or_create(name=DIRECTOR_GROUP)

        # users
        self.owner = User.objects.create_user('owner', password='pass')
        self.owner.groups.add(owner_group)
        self.director = User.objects.create_user('director', password='pass')
        self.director.groups.add(director_group)
        self.other = User.objects.create_user('other', password='pass')

        # create a task table for FK
        self.table = TaskTable.objects.create(name='Class A')  # adapt if constructor differs

        # create activities: past, upcoming (within 7 days), future
        today = date.today()
        Activity.objects.create(title='past', task_table=self.table, assigned_to=self.owner, next_due_date=today - timedelta(days=2), status='open')
        Activity.objects.create(title='soon', task_table=self.table, assigned_to=self.director, next_due_date=today + timedelta(days=3), status='open')
        Activity.objects.create(title='future', task_table=self.table, assigned_to=self.other, next_due_date=today + timedelta(days=30), status='open')

        self.client = APIClient()

    def test_overdue_report_owner(self):
        self.client.login(username='owner', password='pass')
        resp = self.client.get(reverse('overdue-tasks'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        titles = {t['title'] for t in data}
        self.assertIn('past', titles)
        self.assertNotIn('soon', titles)
        self.assertNotIn('future', titles)

    def test_upcoming_report_owner_default_window(self):
        self.client.login(username='owner', password='pass')
        resp = self.client.get(reverse('upcoming-tasks'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        titles = {t['title'] for t in data}
        self.assertIn('soon', titles)
        self.assertNotIn('future', titles)
        self.assertNotIn('past', titles)

    def test_upcoming_report_with_days_param(self):
        self.client.login(username='owner', password='pass')
        resp = self.client.get(reverse('upcoming-tasks') + '?days=60')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        titles = {t['title'] for t in data}
        self.assertIn('future', titles)

    def test_director_can_read_reports_but_cannot_post(self):
        self.client.login(username='director', password='pass')
        resp = self.client.get(reverse('overdue-tasks'))
        self.assertEqual(resp.status_code, 200)
        resp_post = self.client.post(reverse('overdue-tasks'), data={})
        self.assertEqual(resp_post.status_code, 403)

    def test_other_user_denied(self):
        self.client.login(username='other', password='pass')
        resp = self.client.get(reverse('overdue-tasks'))
        self.assertEqual(resp.status_code, 403)
