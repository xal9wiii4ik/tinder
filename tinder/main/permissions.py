from rest_framework.permissions import BasePermission


class IsOwnerOrIsAuthenticated(BasePermission):
    """Permission of is owner or staff for editing"""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return bool(obj.user == request.user or request.user.is_staff)
