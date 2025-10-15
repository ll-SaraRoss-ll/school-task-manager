from rest_framework import permissions
from django.contrib.auth.models import Group

OWNER_GROUP = 'Owner'
DIRECTOR_GROUP = 'Director'

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Owners (users in Owner group) have full access.
    Directors (users in Director group) have read-only access (safe methods).
    All others denied.
    """

    def _in_group(self, user, group_name):
        if not user or not user.is_authenticated:
            return False
        return user.groups.filter(name=group_name).exists()

    def has_permission(self, request, view):
        user = request.user
        if self._in_group(user, OWNER_GROUP):
            return True
        if request.method in permissions.SAFE_METHODS and self._in_group(user, DIRECTOR_GROUP):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
