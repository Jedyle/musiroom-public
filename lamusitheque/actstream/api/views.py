from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from actstream.api.serializers import ActionSerializer
from actstream.models import user_stream, Action

DEFAULT_PER_PAGE = 20


class UserStreamView(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = ActionSerializer

    def get_queryset(self):
        return user_stream(self.request.user, with_user_activity=False)


class AllStreamView(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = ActionSerializer

    def get_queryset(self):
        return Action.objects.all()
