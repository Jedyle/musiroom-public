from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from albums.api.filters import AlbumFilter, ArtistFilter
from albums.api.serializers import (
    GenreSerializer,
    AlbumSerializer,
    ArtistSerializer,
    AlbumGenreSerializer,
    ShortGenreSerializer,
)
from albums.api.service import add_album_details
from albums.models import Genre, Album, Artist, AlbumGenre
from albums.scraper import ParseSimilarArtists, ParseArtist
from albums.settings import SIMILAR_ARTISTS_LENGTH
from musiroom.apiutils.mixins import VoteMixin
from musiroom.apiutils.viewsets import (
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

    @action(detail=True, methods=["GET"])
    def youtube_link(self, request, mbid=None):
        album = self.get_object()
        return Response({"link": album.get_youtube_link()})

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

        similar_from_parser = parser.get_artists()
        values_from_artists_in_db = [
            {"name": artist.name, "mbid": artist.mbid, "image": artist.get_photo()}
            for artist in Artist.objects.filter(
                mbid__in=[el["mbid"] for el in similar_from_parser]
            )
        ]
        artists_in_db = [a["mbid"] for a in values_from_artists_in_db]
        response = []
        for artist in similar_from_parser:
            if artist["mbid"] not in artists_in_db:
                response.append(artist)
        response += values_from_artists_in_db

        return Response({"similar": {"count": len(response), "items": response}})

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


class TopAlbumsView(generics.ListAPIView):
    serializer_class = AlbumSerializer
    pagination_class = None

    def get_queryset(self):
        year = self.kwargs["year"]
        slug = self.kwargs["slug"]
        cache_top = cache.get(f"top_album_albums_{slug}_{year}")
        if cache_top is None:
            albums = Album.objects.get_top(year=year, slug=slug)
            cache.set(
                f"top_album_albums_{slug}_{year}",
                albums,
                timeout=settings.CACHE_TOP_ALBUMS_TIMEOUT,
            )
        else:
            albums = cache_top
        return albums
