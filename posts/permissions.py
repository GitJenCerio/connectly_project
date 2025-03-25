from rest_framework.permissions import BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Allows access only to the author of the object, otherwise read-only.
    """
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = GET, HEAD, OPTIONS
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        # Otherwise must be the author
        return obj.author == request.user

class IsAdminUser(BasePermission):
    """
    Custom permission to only allow admin users to access a particular view.
    """
    def has_permission(self, request, view):
        # Only allow admins (is_staff=True) to access the resource
        return request.user and request.user.is_authenticated and request.user.is_staff

