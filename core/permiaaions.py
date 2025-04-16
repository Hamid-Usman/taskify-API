from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Custom permission to allow only the owner of an object to access or modify it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the object's user field matches the authenticated user
        return obj.user == request.user