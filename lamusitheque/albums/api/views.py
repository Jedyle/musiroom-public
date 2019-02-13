from rest_framework.permissions import IsAuthenticatedOrReadOnly

from albums.api.serializers import GenreSerializer
from albums.models import Genre
from lamusitheque.viewsets import CreateListRetrieveViewSet


class GenreViewSet(CreateListRetrieveViewSet):

    """
    Viewset to create, list and retrieve genres.
    Caution ! When a genre is created, it goes in 'moderated objects' and therefore
    is not visible when calling GET /genres until it is accepted
    """

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = 'slug'
