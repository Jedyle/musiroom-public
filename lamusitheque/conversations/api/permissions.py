from rest_framework import permissions


class IsInConversation(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method is permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user in obj.users.all()


class IsInConversationMessage(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method is permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user in obj.conversation.users.all()
