from django.test import TestCase
from django.contrib.auth import get_user_model
from tasks.models import Task
# Create your tests here.

User = get_user_model()

class TaskModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='sara', password='pass1234')

    def test_task_defaults_and_str(self):
        task = Task.objects.create(
            title='Test Task',
            timeline='short',
            assigned_to=self.user
        )
        self.assertEqual(task.status, 'pending')
        self.assertEqual(str(task), 'Test Task')
