from django.contrib.auth.models import User
from rest_framework import serializers

from conversations.models import Conversation, Message
from user_profile.api.short_serializers import ShortUserSerializer


class ConversationSerializer(serializers.ModelSerializer):
    users = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all(), many=True)

    class Meta:
        model = Conversation
        fields = "__all__"
        read_only_fields = ('archived_by', 'notified', 'unread_by')

    def get_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if user is None:
            raise serializers.ValidationError("User is not logged in")
        return user

    def validate(self, attrs):
        user = self.get_user()
        users = [u for u in attrs.get('users') if u != user]
        if len(users) < 1:
            raise serializers.ValidationError("Discussion must at least contain another user")

        # add request's user to users
        attrs['users'] = users + [user]
        return attrs


class MessageSerializer(serializers.ModelSerializer):

    user = ShortUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('user', 'date', 'last_edit', 'text', 'attachment')







