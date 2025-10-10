from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from tasks.models import TaskTable

User = get_user_model()

class TableEndpointsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_list_retrieve_update_delete_table(self):
        url = reverse('tasktable-list')
        data = {'title': 'Plan A', 'description': 'desc', 'timeline': 'one-off'}
        res = self.client.post(url, data, format='json')
        self.assertEqual(res.status_code, 201)
        table_id = res.data['id']

        list_res = self.client.get(url)
        self.assertEqual(list_res.status_code, 200)

        retrieve_res = self.client.get(reverse('tasktable-detail', args=[table_id]))
        self.assertEqual(retrieve_res.status_code, 200)

        update_res = self.client.put(reverse('tasktable-detail', args=[table_id]),
                                     {'title': 'Plan B', 'description': 'desc', 'timeline': 'yearly'}, format='json')
        self.assertEqual(update_res.status_code, 200)

        del_res = self.client.delete(reverse('tasktable-detail', args=[table_id]))
        self.assertIn(del_res.status_code, (204, 200))
