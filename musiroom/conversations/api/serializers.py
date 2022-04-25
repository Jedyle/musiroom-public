from django.contrib.auth.models import User
from rest_framework import serializers

from conversations.models import Conversation, Message, Membership
from user_profile.api.short_serializers import ShortUserSerializer


class MembershipSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = Membership
        read_only_fields = ("unread", "is_active", "last_read")
        fields = ("user", "unread", "is_active", "last_read")


class ConversationSerializer(serializers.ModelSerializer):

    members = MembershipSerializer(source="membership_set", required=True, many=True)

    last_message_date = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = "__all__"
        read_only_fields = ("archived_by", "notified")

    def create(self, validated_data):
        users = set([el["user"] for el in validated_data.pop("membership_set")])
        conversation = Conversation(**validated_data)
        conversation.save()
        for user in users:
            membership = Membership(user=user, conversation=conversation, unread=True)
            membership.save()
        return conversation

    def update(self, instance, validated_data):
        # we only change membership information, so don"t support changing title for example"
        users = [el["user"] for el in validated_data.pop("membership_set")]
        current_active_users = [
            membership.user
            for membership in Membership.objects.filter(
                conversation=instance, is_active=True
            )
        ]
        added_users = [user for user in users if user not in current_active_users]
        removed_users = [user for user in current_active_users if user not in users]

        for user in added_users:
            membership, _ = Membership.objects.get_or_create(
                user=user, conversation=instance
            )
            membership.is_active = True
            membership.unread = True
            membership.save()
        for user in removed_users:
            membership = Membership.objects.get(conversation=instance, user=user)
            membership.is_active = False
            membership.save()

        instance.save()
        return instance

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
        users = [u for u in attrs.get("membership_set") if u["user"] != user]
        if len(users) < 1:
            raise serializers.ValidationError(
                "Discussion must at least contain another user"
            )

        # add request's user to users
        attrs["membership_set"] = users + [{"user": user}]
        return attrs

    def get_last_message_date(self, obj):
        return (
            obj.messages.order_by("-last_edit").first().last_edit
            if obj.messages.count() > 0
            else None
        )


class MessageSerializer(serializers.ModelSerializer):

    user = ShortUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ("user", "date", "last_edit", "text", "attachment")
