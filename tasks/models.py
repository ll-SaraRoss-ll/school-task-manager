from django.db import models
from django.conf import settings
# Create your models here.

class Task(models.Model):
    TIMELINE_CHOICES = [
        ('short', 'Short Term'),
        ('mid', 'Mid Term'),
        ('long', 'Long Term'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('complete', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    timeline = models.CharField(max_length=10, choices=TIMELINE_CHOICES)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    resources_budget = models.JSONField(default=dict, blank=True)
    performance_indicators = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Activity(models.Model):
    task = models.ForeignKey(Task, related_name='activities', on_delete=models.CASCADE)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Activity on {self.task.title} at {self.timestamp}"