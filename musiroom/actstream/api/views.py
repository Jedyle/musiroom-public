from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from actstream.api.serializers import ActionSerializer
from actstream.models import user_stream, model_stream, Action

from albums.models import Album
from reviews.models import Review
from comments.models import Comment

DEFAULT_PER_PAGE = 20


class UserStreamView(viewsets.GenericViewSet, mixins.ListModelMixin):

    """
    Returns a user's activity stream
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ActionSerializer

    def get_queryset(self):
        return user_stream(self.request.user, with_user_activity=False)


class AbstractPublicStreamView(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = ActionSerializer


class AllStreamView(AbstractPublicStreamView):
    def get_queryset(self):
        return Action.objects.all()


class RatingStreamView(AbstractPublicStreamView):
    def get_queryset(self):
        return model_stream(Album)


class ReviewStreamView(AbstractPublicStreamView):
    def get_queryset(self):
        return model_stream(Review)


class CommentStreamView(AbstractPublicStreamView):
    def get_queryset(self):
        return model_stream(Comment)
