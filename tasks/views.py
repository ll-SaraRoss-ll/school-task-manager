from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import TaskTable, Activity
from .serializers import TaskTableSerializer, ActivitySerializer

class TaskTableViewSet(viewsets.ModelViewSet):
    queryset = TaskTable.objects.all()
    serializer_class = TaskTableSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['timeline']

    def perform_create(self, serializer):
        serializer.save(assigned_to=self.request.user)


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.select_related('task_table').all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['timeline', 'status', 'task_table']
