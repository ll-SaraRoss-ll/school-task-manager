from django.contrib import admin
from .models import TimelineEntry, Activity, TaskTable


# Register your models here.
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'timeline', 'assigned_to', 'next_due_date')
    list_filter = ('status', 'timeline')
    search_fields = ('title', 'description')

@admin.register(TaskTable)
class TaskTableAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'assigned_to', 'timeline')
    list_filter = ('status', 'timeline')
    search_fields = ('title', 'description')

@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    list_display = ('activity', 'old_status', 'new_status', 'changed_at')
    list_filter = ('new_status', 'changed_at')
    search_fields = ('activity__title',)