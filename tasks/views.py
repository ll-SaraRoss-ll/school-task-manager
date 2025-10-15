from collections import defaultdict
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone as dj_timezone

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import TaskTable, Activity, TimelineEntry
from .serializers import (
    TaskTableSerializer,
    ActivitySerializer,
    TimelineEntrySerializer,
    OverdueTaskSerializer,
    UpcomingTaskSerializer,
)
from .permissions import IsOwnerOrReadOnly


class CalendarView(APIView):
    """
    Return timeline entries grouped by date (ISO YYYY-MM-DD).
    Only returns entries whose changed_at is today or later.
    """
    def get(self, request, *args, **kwargs):
        today = dj_timezone.localdate()
        qs = TimelineEntry.objects.filter(changed_at__date__gte=today).select_related('activity')
        serializer = TimelineEntrySerializer(qs, many=True)
        grouped = defaultdict(list)
        for item in serializer.data:
            date_key = item['changed_at'][:10]
            grouped[date_key].append(item)
        return Response(dict(grouped))


class TaskTableViewSet(viewsets.ModelViewSet):
    queryset = TaskTable.objects.all()
    serializer_class = TaskTableSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['timeline']

    def perform_create(self, serializer):
        serializer.save(assigned_to=self.request.user)


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.select_related('task_table', 'assigned_to').all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['timeline', 'status', 'task_table']


@extend_schema(
    summary='Overdue tasks report',
    responses={200: OverdueTaskSerializer(many=True)},
)
class OverdueTasksReportView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request):
        today = dj_timezone.now().date()

        # If Activity has both next_due_date and deadline, return tasks where either is past.
        if hasattr(Activity, 'deadline'):
            qs = Activity.objects.filter(Q(next_due_date__lt=today) | Q(deadline__lt=today))
        else:
            qs = Activity.objects.filter(next_due_date__lt=today)

        qs = qs.select_related('task_table', 'assigned_to')
        serializer = OverdueTaskSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary='Upcoming tasks report',
    parameters=[
        OpenApiParameter(name='days', description='Number of upcoming days to include', required=False, type=int)
    ],
    responses={200: UpcomingTaskSerializer(many=True)},
)
class UpcomingTasksReportView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request):
        try:
            days = int(request.query_params.get('days', 7))
        except (ValueError, TypeError):
            days = 7
        if days < 0:
            days = 7

        today = dj_timezone.now().date()
        end_date = today + timedelta(days=days)
        qs = Activity.objects.filter(next_due_date__gte=today, next_due_date__lte=end_date).select_related('task_table', 'assigned_to')
        serializer = UpcomingTaskSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
