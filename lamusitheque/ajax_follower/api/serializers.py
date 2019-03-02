from rest_framework import serializers


class FollowSerializer(serializers.Serializer):
    user = serializers.CharField(label="User to follow")
