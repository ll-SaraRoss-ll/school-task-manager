from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import TaskTable, Activity
from .serializers import TaskTableSerializer, ActivitySerializer
from collections import defaultdict
from datetime import datetime, timezone

from django.utils import timezone as dj_timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import TimelineEntry
from .serializers import TimelineEntrySerializer

class CalendarView(APIView):
    """
    Return timeline entries grouped by date (ISO YYYY-MM-DD).
    Only returns entries whose changed_at is today or later.
    """
    def get(self, request, *args, **kwargs):
        today = dj_timezone.localdate()
        """
        Performance notes: select_related('activity') used on 
        queryset to avoid per-entry activity lookup if serializer 
        is extended to include activity fields. Use values() 
        if only raw fields are needed.
        """
        qs = TimelineEntry.objects.filter(changed_at__date__gte=today).select_related('activity')
        serializer = TimelineEntrySerializer(qs, many=True)
        grouped = defaultdict(list)
        for item in serializer.data:
            # changed_at comes as ISO datetime string; take date part
            date_key = item['changed_at'][:10]
            grouped[date_key].append(item)
        # Convert defaultdict to normal dict for response
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
    queryset = Activity.objects.select_related('task_table').all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['timeline', 'status', 'task_table']
