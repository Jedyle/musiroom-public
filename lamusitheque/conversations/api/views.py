from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from conversations.api.permissions import IsInConversation, IsInConversationMessage
from conversations.api.serializers import ConversationSerializer, MessageSerializer
from conversations.models import Conversation
from lamusitheque.apiutils.viewsets import CreateListRetrieveUpdateViewset


class ConversationViewset(CreateListRetrieveUpdateViewset):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()
    permission_classes = (IsInConversation,)

    def get_queryset(self):
        return Conversation.objects.filter(users__in=[self.request.user])

    def get_serializer_context(self):
        return {
            "request": self.request
        }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = serializer.save()
        # nobody except the creator read the discussion
        obj.unread_by.add(*obj.users.all())
        obj.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        conv = self.get_object()
        serializer = self.get_serializer(conv, data=request.data)
        serializer.is_valid(raise_exception=True)

        old_users = conv.users.all()
        new_users = serializer.validated_data.get('users')

        added_users = [u for u in new_users if u not in old_users]
        removed_users = [u for u in old_users if u not in new_users]

        obj = serializer.save()
        for added in added_users:
            obj.unread_by.add(added)
        for rem in removed_users:
            obj.unread_by.remove(rem)
        obj.save()
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        conversation = self.get_object()
        conversation.unread_by.remove(user)
        if not conversation.unread_by.exists():
            # all users have read the conversation
            conversation.read_by_all = timezone.now()
            conversation.save()
        return super().retrieve(request, *args, **kwargs)


class MessageViewset(CreateListRetrieveUpdateViewset):
    serializer_class = MessageSerializer
    permission_classes = (IsInConversationMessage,)

    def get_queryset(self):
        conversation_id = self.kwargs['conversations_pk']
        return get_object_or_404(Conversation, id=conversation_id).messages.prefetch_related('user')

    def create(self, request, conversations_pk=None):
        conversation = get_object_or_404(Conversation, pk=conversations_pk)
        if request.user not in conversation.users.all():
            raise PermissionDenied({
                "message": "User is not allowed to access this conversation"
            })

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, conversation_id=conversation.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

