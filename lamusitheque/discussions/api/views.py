from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from discussions.api.filters import DiscussionFilter
from discussions.api.serializers import DiscussionSerializer
from discussions.models import Discussion
from lamusitheque.apiutils.permissions import IsUserOrReadOnly
from lamusitheque.apiutils.serializers import VoteSerializer


class DiscussionViewset(viewsets.ModelViewSet):

    """
    Possible list queries :
        api/discussions/?content_type__model=album
                        ?content_type_id__isnull=true/false
                        ?object_id=4
    """

    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer
    permission_classes = (IsUserOrReadOnly,)
    filter_class = DiscussionFilter
    ordering_fields = ('vote_score', 'created')

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["PUT"])
    def vote(self, request, pk=None):
        # votes
        # TODO : change default form in browsable API
        # TODO : refactor with other votes
        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote = serializer.validated_data.get('vote')
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
        return Response(serializer.data)


class UserDiscussionViewset(viewsets.GenericViewSet, mixins.ListModelMixin):

    """
    View to list a user's discussions
    """

    serializer_class = DiscussionSerializer
    permission_classes = (IsUserOrReadOnly,)
    filter_class = DiscussionFilter

    def get_queryset(self):
        username = self.kwargs["users_user__username"]
        return Discussion.objects.filter(user__username=username)
