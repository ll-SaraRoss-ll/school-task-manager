from django.db import models
from django.conf import settings
from .utils import get_next_yearly_date, get_next_quarter_dates, get_next_term_dates
from datetime import date

# Create your models here.

TIMELINE_CHOICES = (
    ('one-off', 'One-off'),
    ('yearly', 'Yearly'),
    ('quarterly', 'Quarterly'),
    ('term', 'Term'),
)

class TaskTable(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('complete', 'Completed'),
    ]

    #title = models.CharField(max_length=200)
    title = models.CharField(max_length=255, null=True, blank=True)
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
    # Make task_table nullable for incremental migration; backfill existing rows, then remove null=True if you want it required.
    task_table = models.ForeignKey(TaskTable, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    timeline = models.CharField(max_length=32, choices=TIMELINE_CHOICES, default='one-off')
    assigned_to = models.CharField(max_length=255, blank=True, null=True)
    resources_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    performance_indicators = models.TextField(blank=True)
    status = models.CharField(max_length=64, default='pending')
    next_due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_next_due(self):
        today = date.today()
        if self.timeline == 'yearly':
            return get_next_yearly_date(today)
        if self.timeline == 'quarterly':
            q = get_next_quarter_dates(today)
            return q[0] if q else None
        if self.timeline == 'term':
            t = get_next_term_dates(today)
            return t[0] if t else None
        return None

    def save(self, *args, **kwargs):
        if not self.pk and self.timeline != 'one-off':
            # only set next_due_date on create for recurring timelines
            next_due = self.calculate_next_due()
            if next_due:
                self.next_due_date = next_due
        super().save(*args, **kwargs)
