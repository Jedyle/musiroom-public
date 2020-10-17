from django.contrib.auth.models import User
from rest_framework import serializers


class ShortUserSerializer(serializers.ModelSerializer):

    avatar = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("username", "avatar", "description")

    def get_avatar(self, obj):
        return obj.profile.get_avatar()

    def get_description(self, obj):
        return obj.profile.description
