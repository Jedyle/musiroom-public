from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from conversations.api.permissions import (
    IsInConversation,
    IsInConversationMessage,
    user_is_active_in_conversation,
)
from conversations.api.serializers import ConversationSerializer, MessageSerializer
from conversations.models import Conversation
from musiroom.apiutils.viewsets import CreateListRetrieveUpdateViewset
from rest_framework.exceptions import PermissionDenied


class ConversationViewset(CreateListRetrieveUpdateViewset):
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()
    permission_classes = (IsInConversation,)

    def get_queryset(self):
        return Conversation.objects.filter(users__in=[self.request.user])

    def get_serializer_context(self):
        return {"request": self.request}


class MessageViewset(CreateListRetrieveUpdateViewset):
    serializer_class = MessageSerializer
    permission_classes = (IsInConversationMessage,)

    def get_queryset(self):
        conversation_id = self.kwargs["conversations_pk"]
        conversation = get_object_or_404(Conversation, id=conversation_id)
        messages = conversation.messages
        user_membership = conversation.membership_set.get(user=self.request.user)
        if user_membership.is_active is False:
            messages = messages.filter(date__lte=user_membership.last_read)
        return messages.prefetch_related("user").order_by("-date")

    def list(self, request, conversations_pk=None, *args, **kwargs):
        response = super().list(
            request, conversations_pk=conversations_pk, *args, **kwargs
        )
        # this needs to be after, because get_queryset above checks the 'last_read' value
        conversation = get_object_or_404(Conversation, pk=conversations_pk)
        user_membership = conversation.membership_set.get(user=self.request.user)
        page = request.GET.get("page")
        if (str(page) == "1" or page is None) and user_membership.is_active:
            conversations = get_object_or_404(Conversation, pk=conversations_pk)
            conversations.mark_as_read(request.user)
        return response

    def create(self, request, conversations_pk=None):
        conversation = get_object_or_404(Conversation, pk=conversations_pk)
        if not user_is_active_in_conversation(request.user, conversation):
            raise PermissionDenied()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(user=request.user, conversation_id=conversation.id)
        message.conversation.mark_unread_by_all_except(request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
