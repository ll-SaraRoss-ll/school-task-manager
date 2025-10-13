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
    STATUS_CHOICES = (
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    )
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

    def __str__(self):
        """
        human-friendly string for activity used by tests and admin.
        returns the title if available, otherwise a fallback with the id.
        """
        return self.title or f"Activity {self.pk}"

class TimelineEntry(models.Model):
    """
    TimelineEntry records every status transition for an Activity.
    Each record captures the activity, the previous and new status,
    the timestamp when the change was recorded, and optional metadata
    for auditing (for example: user id, reason, request id).
    """
    activity = models.ForeignKey(
        'Activity',
        on_delete=models.CASCADE,
        related_name='timeline_entries'
    )  # The Activity this timeline entry belongs to

    old_status = models.CharField(
        max_length=20,
        choices=Activity.STATUS_CHOICES
    )  # Status value before the change

    new_status = models.CharField(
        max_length=20,
        choices=Activity.STATUS_CHOICES
    )  # Status value after the change

    changed_at = models.DateTimeField(
        auto_now_add=True
    )  # When the status change was recorded

    metadata = models.JSONField(
        blank=True,
        null=True
    )  # Optional JSON blob with extra info (user, IP, request id, reason)

    class Meta:
        ordering = ('-changed_at',)

    def __str__(self):
        return f"TimelineEntry(activity_id={self.activity_id}, {self.old_status}→{self.new_status} at {self.changed_at})"


# Backwards-compatibility alias: tests or older code expect `Task`.
# Ensure `Task` always exists and points to the Activity model.
if 'Task' not in globals():
    if 'Activity' in globals():
        Task = Activity
    else:
        # fallback: create a simple alias to avoid NameError during imports
        class Task(models.Model):
            class Meta:
                managed = False
                app_label = 'tasks'
