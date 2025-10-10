from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TaskTableViewSet, ActivityViewSet

router = DefaultRouter()
router.register(r'tables', TaskTableViewSet, basename='tasktable')
router.register(r'activities', ActivityViewSet, basename='activity')

urlpatterns = [
    path('', include(router.urls)),
]
