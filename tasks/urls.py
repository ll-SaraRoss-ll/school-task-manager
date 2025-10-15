from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TaskTableViewSet, ActivityViewSet
from .views import CalendarView
from .views import OverdueTasksReportView, UpcomingTasksReportView


router = DefaultRouter()
router.register(r'tables', TaskTableViewSet, basename='tasktable')
router.register(r'activities', ActivityViewSet, basename='activity')

urlpatterns = [
    path('reports/overdue/', OverdueTasksReportView.as_view(), name='overdue-tasks'),
    path('reports/upcoming/', UpcomingTasksReportView.as_view(), name='upcoming-tasks'),
    path('', include(router.urls)),
    path('calendar/', CalendarView.as_view(), name='calendar'),
]
