from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from tasks.models import Activity

class Command(BaseCommand):
    help = 'Create Owner and Director groups with appropriate permissions'

    def handle(self, *args, **options):
        owner, _ = Group.objects.get_or_create(name='Owner')
        director, _ = Group.objects.get_or_create(name='Director')
        ct = ContentType.objects.get_for_model(Activity)

        perms_owner = Permission.objects.filter(content_type=ct)
        owner.permissions.set(perms_owner)

        view_perm = Permission.objects.get(content_type=ct, codename='view_activity')
        director.permissions.set([view_perm])

        self.stdout.write(self.style.SUCCESS('Owner and Director groups created/updated'))
