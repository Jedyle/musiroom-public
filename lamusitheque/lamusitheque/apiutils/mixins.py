from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from lamusitheque.apiutils.serializers import VoteSerializer


class VoteMixin(object):

    """
    Mixin with a custom action to vote
    """

    @action(detail=True, methods=["PUT"])
    def vote(self, request, **kwargs):
        # votes
        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote = serializer.validated_data.get("vote")
        obj = self.get_object()
        if vote == "up":
            obj.votes.up(request.user.pk)
        elif vote == "down":
            obj.votes.down(request.user.pk)
        else:
            obj.votes.delete(request.user.pk)
        # re-call get object to have the updated instance
        # (doesn't update by itself, don't know why)
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        print(serializer.__class__)
        return Response(serializer.data)


class VoteSerializerMixin(serializers.Serializer):

    user_vote = serializers.SerializerMethodField(read_only=True)

    def get_user_vote(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            vote = obj.votes.get(request.user.id)
            votes_mapping = {0: "up", 1: "down"}
            return votes_mapping.get(vote.action) if vote else None
        else:
            return None
