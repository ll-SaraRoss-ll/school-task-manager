from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from .models import TimelineEntry, Activity

@receiver(pre_save, sender=Activity)
def log_activity_status_change(sender, instance, **kwargs):
    """
    On Activity save, if the status changed compared to DB value,
    create a TimelineEntry recording old_status, new_status, and
    optional metadata. Metadata can be extended by middleware or
    the caller before save (e.g., instance._status_change_metadata).
    """
    if instance.pk is None:
        # New object, no previous status to log
        return

    try:
        old = sender.objects.only('status').get(pk=instance.pk)
    except ObjectDoesNotExist:
        return

    old_status = old.status
    new_status = instance.status

    if old_status != new_status:
        # Allow callers to attach metadata to instance prior to save:
        metadata = getattr(instance, '_status_change_metadata', None)
        TimelineEntry.objects.create(
            activity=instance,
            old_status=old_status,
            new_status=new_status,
            metadata=metadata
        )
