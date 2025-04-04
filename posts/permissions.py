from rest_framework.permissions import BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """
    Allows access only to the author of the object, otherwise read-only.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.author == request.user
    
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD') or request.user.is_authenticated and request.user.is_staff

class IsAuthorOrAdmin(BasePermission):
    """
    Allow access to authors and admin users only.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff

