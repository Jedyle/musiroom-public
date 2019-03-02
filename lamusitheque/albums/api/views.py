import re

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from albums.api.filters import AlbumFilter
from albums.api.serializers import GenreSerializer, AlbumSerializer, ArtistSerializer, AlbumGenreSerializer, \
    UserInterestSerializer
from albums.models import Genre, Album, Artist, AlbumGenre, UserInterest
from albums.scraper import ParseSimilarArtists, ParseArtist
from lamusitheque.apiutils.serializers import VoteSerializer
from lamusitheque.apiutils.viewsets import CreateListRetrieveViewset, ListRetrieveViewset


class GenreViewset(CreateListRetrieveViewset):
    """
    Viewset to create, list and retrieve genres.
    Caution ! When a genre is created, it goes in 'moderated objects' and therefore
    is not visible when calling GET /genres until it is accepted
    """

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = 'slug'


class AlbumViewset(ListRetrieveViewset):
    serializer_class = AlbumSerializer
    queryset = Album.objects.all()
    lookup_field = 'mbid'
    filter_class = AlbumFilter

    def get_object(self):
        """
        Loads album from database if exists, else gets album from musicbrainz.
        """
        mbid = self.kwargs["mbid"]
        return Album.objects.get_from_api(mbid)

    @action(detail=True, methods=['GET'])
    def real_genres(self, request, mbid=None):
        album = self.get_object()
        album_genres = album.genres.filter(albumgenre__is_genre=True).order_by("albumgenre__vote_score")
        serializer = GenreSerializer(album_genres, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        return {
            "request": self.request
        }

    @action(detail=True, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def user_interest(self, request, mbid=None):
        album = self.get_object()
        if request.method == "GET":
            return Response({
                "user": request.user.username,
                "interest": album.users_interested.filter(username=request.user.username).exists()
            })
        elif request.method == "PUT":
            serializer = UserInterestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            value = serializer.validated_data.get('value')
            # add user interest (or get it if exists)
            user_interest, created = UserInterest.objects.get_or_create(album=album, user=request.user)
            if not value:  # if value=false, delete
                user_interest.delete()
            return Response({
                "user": request.user.username,
                "interest": value
            })


class AlbumGenreViewset(CreateListRetrieveViewset):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = AlbumGenreSerializer
    lookup_field = "genre__slug"

    def get_queryset(self):
        album = get_object_or_404(Album, mbid=self.kwargs['albums_mbid'])
        return AlbumGenre.objects.filter(album=album)

    def get_object(self):
        mbid = self.kwargs['albums_mbid']
        slug = self.kwargs['genre__slug']
        albumgenre = get_object_or_404(AlbumGenre, album__mbid=mbid, genre__slug=slug)
        return albumgenre

    def get_serializer_context(self):
        return {'request': self.request,
                'mbid': self.kwargs.get('albums_mbid')}

    @action(detail=True, methods=['PUT'])
    def vote(self, request, albums_mbid=None, genre__slug=None):
        # votes
        # TODO : change default form in browsable API
        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote = serializer.validated_data.get('vote')
        album_genre = self.get_object()
        if vote in ["up", "down"]:
            getattr(album_genre.votes, vote)(request.user.pk)
        else:
            album_genre.votes.delete(request.user.pk)
        serializer = self.get_serializer(album_genre)
        return Response(serializer.data)


class ArtistViewset(ListRetrieveViewset):
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()
    lookup_field = "mbid"

    def get_object(self):
        mbid = self.kwargs['mbid']
        try:
            artist = Artist.objects.get_from_api(mbid)
        except Artist.DoesNotExist:
            raise Http404

    @action(detail=True, methods=['get'])
    def similar(self, request, mbid=None):
        artist = self.get_object()
        # default number of artists to send
        # TODO : define global variable for limit (no hardcoded variable)+
        limit = int(request.query_params.get('limit', 6))
        parser = ParseSimilarArtists(artist.mbid, limit=limit)
        if not parser.load():
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ArtistSerializer(artist)
        similar = parser.get_artists()
        return Response({
            **serializer.data,
            "similar": {
                "count": len(similar),
                "items": similar
            }
        })

    @action(detail=True, methods=["GET"])
    def discography(self, request, mbid=None):

        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            page = 1

        name = request.GET.get('search', '')
        parser = ParseArtist(mbid, page=page, name=name)
        if not parser.load():
            raise Http404
        discog = parser.get_discography()
        artist_name = parser.get_name()
        nb_pages = parser.get_nb_pages()

        return Response({
            "results": discog,
            "artist": artist_name,
            "mbid": mbid,
            "num_pages": nb_pages,
            "page": page,
            "search": ""
        })


SLUG_ALL_VALUE = "all"
YEAR_ALL_VALUE = "all"


class TopAlbumsView(generics.ListAPIView):
    serializer_class = AlbumSerializer

    def get_queryset(self):
        year = self.kwargs['year']
        slug = self.kwargs['slug']
        albums = Album.objects.all()
        if year != YEAR_ALL_VALUE:
            m = re.match(r'^([0-9]{4})s$', year)
            if m is not None:
                decade = int(m.group(1))
                years = [(decade + i) for i in range(10)]
            else:
                years = [int(year)]
            albums = albums.filter(release_date__year__in=years)

        if slug != SLUG_ALL_VALUE:
            genre = Genre.objects.get(slug=slug)
            associated_genres = genre.get_all_children()
            albums = albums.filter(Q(albumgenre__genre__in=associated_genres) & Q(albumgenre__is_genre=True))

        albums = albums.filter(
            Q(ratings__isnull=False) & Q(ratings__average__gt=1.0) & Q(ratings__count__gt=2)).order_by(
            '-ratings__average', 'title')

        cache_albums = cache.get('top_album_albums_{}_{}'.format(slug, year))
        if cache_albums is None:
            albums = albums.distinct().prefetch_related('artists')[:100]
            cache.set('top_album_albums_{}_{}'.format(slug, year), albums)
        else:
            albums = cache_albums

        return albums


class UserInterestsViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = AlbumSerializer

    def get_queryset(self):
        username = self.kwargs['users_user__username']
        user = get_object_or_404(User, username=username)
        return user.interests.all()
