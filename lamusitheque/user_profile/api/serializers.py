from django.contrib.auth.models import User
from generic_relations.relations import GenericRelatedField
from star_ratings.models import UserRating
from notifications.models import Notification
from pinax.badges.models import BadgeAward
from rest_framework import serializers
from reviews.models import Review

from user_profile.models import Profile
from discussions.models import Discussion
from discussions.api.serializers import DiscussionSerializer
from reviews.api.serializers import ReviewSerializer
from comments.models import Comment
from comments.api.short_serializers import ShortCommentSerializer

from .short_serializers import ShortUserSerializer

# TODO : change email template to reset a password (switch to english)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ("user", "top_albums")
        read_only_fields = ("avatar",)


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "profile")
        read_only_fields = ("username",)

    def update(self, instance, validated_data):
        print(validated_data)
        profile = instance.profile

        profile_data = validated_data.pop("profile")
        for key in profile_data:
            setattr(profile, key, profile_data[key])
        profile.save()
        for key in validated_data:
            setattr(instance, key, validated_data[key])
        instance.save()
        return instance


class ProfileAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("avatar",)


class CreateUserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "username", "password", "password_confirm")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(email=validated_data["email"], username=validated_data["username"])
        user.set_password(validated_data["password"])
        # not active until email is confirmed
        user.is_active = False
        # save() triggers a signal responsible for creating user_profile and other data
        user.save()
        return user

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords does not match")
        return attrs


class PasswordConfirmSerializer(serializers.ModelSerializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    password = serializers.CharField(max_length=128)

    class Meta:
        model = User
        fields = ("password",)


class PublicProfileSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(
        slug_field="username", many=False, read_only=True
    )
    first_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()
    birth = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    nb_ratings = serializers.SerializerMethodField()
    nb_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        exclude = ("display_birth", "display_name", "display_sex", "top_albums")
        lookup_field = "user__username"

    def get_nb_ratings(self, profile):
        return UserRating.objects.filter(user=profile.user).count()

    def get_nb_reviews(self, profile):
        return Review.objects.filter(rating__user=profile.user).count()

    def get_avatar(self, profile):
        return profile.get_avatar()

    def get_date_joined(self, profile):
        return profile.user.date_joined

    def get_first_name(self, profile):
        if profile.display_name:
            return profile.user.first_name
        return None

    def get_birth(self, profile):
        return profile.birth if profile.display_birth else None

    def get_sex(self, profile):
        return profile.get_sex_display() if profile.display_sex else None


class NotificationSerializer(serializers.ModelSerializer):

    actor = GenericRelatedField({User: ShortUserSerializer()})

    target_content_type = serializers.SlugRelatedField(
        slug_field="model", read_only=True
    )
    target = GenericRelatedField(
        {
            Comment: ShortCommentSerializer(),
            Discussion: DiscussionSerializer(),
            Review: ReviewSerializer()
        }
    )

    class Meta:
        model = Notification
        fields = (
            "id",
            "unread",
            "timestamp",
            "actor",
            "target_content_type",
            "target_object_id",
            "verb",
            "target",
            "deleted"
        )


class BadgeSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()

    class Meta:
        model = BadgeAward
        fields = ("name", "description", "progress", "image")

    def get_image(self, obj):
        return obj._badge.images[obj.level]
