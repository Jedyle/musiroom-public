from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import MethodNotAllowed

from albums.api.serializers import ShortAlbumSerializer, ShortArtistSerializer
from discussions.api.filters import DiscussionFilter
from discussions.api.serializers import DiscussionSerializer, DiscussionUpdateSerializer
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

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.request.method in ['PUT', 'PATCH']:
            serializer_class = DiscussionUpdateSerializer

        return serializer_class

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, *args, **kwargs):
        raise MethodNotAllowed("POST", detail="Use PATCH")

    def partial_update(self, request, *args, **kwargs):
        return super().update(request, *args, partial=True, **kwargs)

    
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


@api_view(["GET"])
def get_discussion_object(request, model, object_id):
    model_klass = get_object_or_404(ContentType, model=model).model_class()
    dobject = get_object_or_404(model_klass, id=object_id)
    print(dobject, model)
    serializer = ShortAlbumSerializer if model == 'album' else ShortArtistSerializer
    return Response({
        "object": serializer(dobject).data,
        "model": model
    })
