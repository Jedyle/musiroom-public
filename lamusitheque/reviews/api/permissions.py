from rest_framework import permissions

from lamusitheque.apiutils.permissions import REGULAR_ACTIONS


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow author of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif view.action not in REGULAR_ACTIONS:
            return True
        else:
            return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        elif view.action not in REGULAR_ACTIONS:
            return True
        # Instance must have an attribute named `owner`.
        return obj.rating.user == request.user
