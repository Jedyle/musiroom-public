from django.contrib.auth.models import User
from notifications.models import Notification
from pinax.badges.models import BadgeAward
from rest_framework import serializers

from user_profile.models import Profile


# TODO : change email template to reset a password (switch to english)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('user', 'top_albums')


class ShortUserSerializer(serializers.ModelSerializer):

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'avatar')

    def get_avatar(self, obj):
        return obj.profile.get_avatar()


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'profile')
        read_only_fields = ('username',)

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('user_profile')
        profile = instance.profile

        # check avatar is not None
        avatar = profile_data.pop('avatar', None)
        if avatar is not None:
            profile.avatar = avatar

        for key in profile_data:
            setattr(profile, key, profile_data[key])
        profile.save()
        for key in validated_data:
            setattr(instance, key, validated_data[key])
        instance.save()
        return instance


class CreateUserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
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
        fields = ('password',)


class PublicProfileSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(slug_field="username", many=False, read_only=True)
    first_name = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()
    birth = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        exclude = ('display_birth', 'display_name', 'display_sex', 'top_albums')
        lookup_field = 'user__username'

    def get_date_joined(self, obj):
        return obj.user.date_joined

    def get_first_name(self, obj):
        if obj.display_name:
            return obj.user.first_name
        return None

    def get_birth(self, obj):
        return obj.birth if obj.display_birth else None

    def get_sex(self, obj):
        return obj.get_sex_display() if obj.display_sex else None


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = "__all__"


class BadgeSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()

    class Meta:
        model = BadgeAward
        fields = ('name', 'description', 'progress', 'image')

    def get_image(self, obj):
        return obj._badge.images[obj.level]
