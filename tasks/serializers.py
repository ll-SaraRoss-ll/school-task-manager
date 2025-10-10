from rest_framework import serializers
from .models import TaskTable, Activity

class ActivitySerializer(serializers.ModelSerializer):
    table_title = serializers.CharField(source='task_table.title', read_only=True)
    next_due_date = serializers.DateField(read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Activity
        fields = [
            'id',
            'task_table',
            'table_title',
            'title',
            'description',
            'timeline',
            'assigned_to',
            'resources_budget',
            'performance_indicators',
            'status',
            'next_due_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'next_due_date', 'table_title']


class TaskTableSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(many=True, read_only=True)

    class Meta:
        model = TaskTable
        fields = [
            'id',
            'title',
            'description',
            'timeline',
            'created_at',
            'updated_at',
            'activities',
        ]
        read_only_fields = ['created_at', 'updated_at', 'activities']
