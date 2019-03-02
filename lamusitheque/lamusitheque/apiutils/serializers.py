from rest_framework import serializers


class VoteSerializer(serializers.Serializer):
    vote = serializers.ChoiceField(["up", "down", "null"])
