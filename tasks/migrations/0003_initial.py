# tasks/migrations/0003_auto_resolve_renames.py
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_initial'),
    ]

    operations = [
        # Rename model Task -> TaskTable
        migrations.RenameModel(
            old_name='Task',
            new_name='TaskTable',
        ),

        # Rename Activity field 'timestamp' -> 'created_at'
        migrations.RenameField(
            model_name='activity',
            old_name='timestamp',
            new_name='created_at',
        ),

        # Rename Activity field 'task' -> 'task_table'
        migrations.RenameField(
            model_name='activity',
            old_name='task',
            new_name='task_table',
        ),
    ]
