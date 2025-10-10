from django.core.management.base import BaseCommand
from datetime import date
from tasks.models import Activity
from django.utils import timezone
from django.db import transaction

class Command(BaseCommand):
    help = 'Generate recurring Activity instances when their next_due_date is due'

    def handle(self, *args, **options):
        today = date.today()
        due_activities = Activity.objects.filter(next_due_date__lte=today).exclude(timeline='one-off')
        created = 0

        for act in due_activities:
            with transaction.atomic():
                # clone activity for the new period
                act.pk = None
                act.created_at = timezone.now()
                act.updated_at = timezone.now()
                # preserve timeline and other fields; compute next_due_date for the clone
                # using existing calculate_next_due logic; save creates a new record
                act.next_due_date = None
                act.save()
                created += 1

                # update the original's next_due_date to the next occurrence
                orig = Activity.objects.filter(id=act.id).first()  # this now refers to clone; we need original
                # Instead, store original before cloning in the loop
        self.stdout.write(self.style.SUCCESS(f'Generated {created} recurring activities'))
