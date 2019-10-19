from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from discussions.api.filters import DiscussionFilter
from discussions.api.serializers import DiscussionSerializer
from discussions.models import Discussion
from lamusitheque.apiutils.mixins import VoteMixin
from lamusitheque.apiutils.permissions import IsUserOrReadOnly


class DiscussionViewset(viewsets.ModelViewSet, VoteMixin):
    """
    Discussions
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
