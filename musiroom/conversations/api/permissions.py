from rest_framework import permissions
from conversations.models import Membership
from rest_framework.exceptions import PermissionDenied


def user_is_in_conversation(user, conversation):
    return user in conversation.users.all()


def user_is_active_in_conversation(user, conversation):
    return Membership.objects.filter(
        conversation=conversation, user=user, is_active=True
    ).exists()


class IsInConversation(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return user_is_in_conversation(request.user, obj)
        return user_is_active_in_conversation(request.user, obj)


class IsInConversationMessage(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method is permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return user_is_in_conversation(request.user, obj.conversation)
        return user_is_active_in_conversation(request.user, obj.conversation)
