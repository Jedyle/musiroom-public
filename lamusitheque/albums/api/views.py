import re

from youtube_api import YouTubeDataAPI
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, mixins
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from albums.api.filters import AlbumFilter, ArtistFilter
from albums.api.serializers import (
    GenreSerializer,
    AlbumSerializer,
    ArtistSerializer,
    AlbumGenreSerializer,
    UserInterestSerializer,
    ShortGenreSerializer,
)
from albums.api.service import add_album_details
from albums.models import Genre, Album, Artist, AlbumGenre, UserInterest
from albums.scraper import ParseSimilarArtists, ParseArtist
from albums.settings import SIMILAR_ARTISTS_LENGTH
from lamusitheque.apiutils.mixins import VoteMixin
from lamusitheque.apiutils.viewsets import (
    CreateListRetrieveViewset,
    ListRetrieveViewset,
    ListViewset,
)


class GenreViewset(CreateListRetrieveViewset):
    """
    Creates, lists and retrieves genres.
    When a genre is created, it is not publicly available until a moderator approves it.
    """

    pagination_class = None
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = "slug"

    def get_queryset(self):
        # if asked a list, we directly display a tree
        if self.action == "list":
            return Genre.objects.filter(parent__isnull=True)
        elif self.action == "create":
            return Genre.unmoderated_objects.all()
        return Genre.objects.all()


class GenreListViewset(ListViewset):

    serializer_class = ShortGenreSerializer
    pagination_class = None
    lookup_field = "slug"

    def get_queryset(self):
        """
        Required to initialize app, because django-moderation reads this value
        """
        return Genre.objects.all()


class AlbumViewset(ListRetrieveViewset):

    """
    Lists and retrieves albums.
    """

    serializer_class = AlbumSerializer
    queryset = Album.objects.all()
    lookup_field = "mbid"
    filter_class = AlbumFilter

    def get_object(self):
        """
        Loads album from database if exists, else gets album from musicbrainz.
        """
        mbid = self.kwargs["mbid"]
        album = Album.objects.get_from_api(mbid)
        self.check_object_permissions(self.request, album)
        return album

    @action(detail=False, methods=["GET"])
    @method_decorator(cache_page(60 * 60))
    def latest(self, request):
        albums = (
            Album.objects.filter(release_date__isnull=False, cover__isnull=False)
            .exclude(cover__exact="")
            .order_by("-release_date")[:18]
        )
        serializer = self.get_serializer(albums, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def real_genres(self, request, mbid=None):

        """
        List an album's genres (the 3 most voted genres for the album).
        """

        album = self.get_object()
        serializer = GenreSerializer(album.real_genres, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=True, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])
    def user_interest(self, request, mbid=None):
        """
        If method = GET, returns whether the user has added the album in his 'interests' list.
        If method = PUT, adds or delete the album in his 'interests' list, based on a 'value'
        field in the form (true or false).
        """
        album = self.get_object()
        if request.method == "GET":
            return Response(
                {
                    "user": request.user.username,
                    "interest": album.users_interested.filter(
                        username=request.user.username
                    ).exists(),
                }
            )
        elif request.method == "PUT":
            serializer = UserInterestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            value = serializer.validated_data.get("value")
            # add user interest (or get it if exists)
            user_interest, created = UserInterest.objects.get_or_create(
                album=album, user=request.user
            )
            if not value:  # if value=false, delete
                user_interest.delete()
            return Response({"user": request.user.username, "interest": value})

    @action(detail=True, methods=["GET"])
    def youtube_link(self, request, mbid=None):
        album = self.get_object()
        search_string = f"{album.artists.first().name} {album.title}"
        yt = YouTubeDataAPI(settings.YOUTUBE_API_KEY)
        res = yt.search(search_string, max_results=1)
        return Response({"link": f"https://youtube.com/watch?v={res[0]['video_id']}"})

    @action(detail=True, methods=["GET"])
    def same_artist(self, request, mbid=None):
        album = self.get_object()
        queryset = self.queryset.filter(artists__in=album.artists.all()).exclude(
            mbid=mbid
        )[:3]
        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data})


class AlbumGenreViewset(CreateListRetrieveViewset, VoteMixin):

    """
    Genre suggestion for an album.
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = AlbumGenreSerializer
    pagination_class = None
    lookup_field = "genre__slug"

    def get_queryset(self):
        album = get_object_or_404(Album, mbid=self.kwargs["albums_mbid"])
        return AlbumGenre.objects.filter(album=album)

    def get_object(self):
        mbid = self.kwargs["albums_mbid"]
        slug = self.kwargs["genre__slug"]
        albumgenre = get_object_or_404(AlbumGenre, album__mbid=mbid, genre__slug=slug)
        self.check_object_permissions(self.request, albumgenre)
        return albumgenre

    def get_serializer_context(self):
        return {"request": self.request, "mbid": self.kwargs.get("albums_mbid")}


class ArtistViewset(ListRetrieveViewset):

    """
    Lists and retrieves artists.
    """

    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()
    lookup_field = "mbid"
    filter_class = ArtistFilter

    def get_object(self):
        mbid = self.kwargs["mbid"]
        try:
            artist = Artist.objects.get_from_api(mbid)
        except Artist.DoesNotExist:
            raise Http404
        self.check_object_permissions(self.request, artist)
        return artist

    @action(detail=True, methods=["GET"])
    def similar(self, request, mbid=None):

        """
        Lists similar artists
        """

        artist = self.get_object()
        # default number of artists to send
        limit = int(request.query_params.get("limit", SIMILAR_ARTISTS_LENGTH))
        parser = ParseSimilarArtists(artist.mbid, limit=limit)
        if not parser.load():
            return Response(status=status.HTTP_404_NOT_FOUND)
        similar = parser.get_artists()
        return Response({"similar": {"count": len(similar), "items": similar}})

    @action(detail=True, methods=["GET"])
    def discography(self, request, mbid=None):

        """
        Lists an artist's discography
        """

        try:
            page = int(request.GET.get("page", 1))
        except ValueError:
            page = 1

        name = request.GET.get("search", "")
        parser = ParseArtist(mbid, page=page, name=name)
        if not parser.load():
            raise Http404
        discog = parser.get_discography()
        discog = add_album_details(discog, request)

        artist_name = parser.get_name()
        nb_pages = parser.get_nb_pages()

        return Response(
            {
                "results": discog,
                "artist": artist_name,
                "mbid": mbid,
                "num_pages": nb_pages,
                "page": page,
                "search": "",
            }
        )


SLUG_ALL_VALUE = "all"
YEAR_ALL_VALUE = "all"


class TopAlbumsView(generics.ListAPIView):
    serializer_class = AlbumSerializer
    pagination_class = None

    def get_queryset(self):
        year = self.kwargs["year"]
        slug = self.kwargs["slug"]
        albums = Album.objects.all()
        if year != YEAR_ALL_VALUE:
            m = re.match(r"^([0-9]{4})s$", year)
            if m is not None:
                decade = int(m.group(1))
                years = [(decade + i) for i in range(10)]
            else:
                years = [int(year)]
            albums = albums.filter(release_date__year__in=years)

        if slug != SLUG_ALL_VALUE:
            genre = get_object_or_404(Genre, slug=slug)
            associated_genres = genre.get_all_children()
            albums = albums.filter(
                Q(albumgenre__genre__in=associated_genres)
                & Q(albumgenre__is_genre=True)
            )

        albums = albums.filter(
            Q(ratings__isnull=False)
            & Q(ratings__average__gt=1.0)
            & Q(ratings__count__gt=2)
        ).order_by("-ratings__average", "title")

        cache_albums = cache.get("top_album_albums_{}_{}".format(slug, year))
        if cache_albums is None:
            albums = albums.distinct().prefetch_related("artists")[:100]
            cache.set("top_album_albums_{}_{}".format(slug, year), albums)
        else:
            albums = cache_albums

        return albums


class UserInterestsViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = AlbumSerializer

    def get_queryset(self):
        username = self.kwargs["users_user__username"]
        user = get_object_or_404(User, username=username)
        album_title = self.request.query_params.get("album_title__icontains")
        queryset = user.interests
        if album_title:
            queryset = queryset.filter(title__icontains=album_title)
        return queryset.all()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_interests(request):
    ids = request.GET.get("ids", [])
    if ids == "":
        ids = []
    elif ids is not None:
        try:
            ids = [int(el) for el in ids.split(",")]
        except ValueError:
            return Response(
                {"message": "IDs are not integers"}, status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(
            {"message": "Parameter 'ids' is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = request.user
    interests_list = UserInterest.objects.filter(user=user, album__ratings__id__in=ids)
    return Response({"interests": [el.album.ratings.get().id for el in interests_list]})
