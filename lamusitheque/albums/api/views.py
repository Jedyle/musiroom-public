from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from albums.api.filters import AlbumFilter
from albums.api.serializers import GenreSerializer, AlbumSerializer, ArtistSerializer, AlbumGenreSerializer, \
    VoteSerializer
from albums.models import Genre, Album, Artist, AlbumGenre
from albums.scraper import ParseSimilarArtists
from albums.views import load_album_if_not_exists, create_artist_from_mbid
from lamusitheque.viewsets import CreateListRetrieveViewset, ListRetrieveViewset


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
        try:
            album = Album.objects.get(mbid=mbid)
        except Album.DoesNotExist:
            album, artists = load_album_if_not_exists(mbid)
        if album is None:
            raise Http404("Album does not exist")
        return album

    @action(detail=True, methods=['GET'])
    def real_genres(self, request, mbid=None):
        album = self.get_object()
        album_genres = album.genres.filter(albumgenre__is_genre=True).order_by("albumgenre__vote_score")
        serializer = GenreSerializer(album_genres, many=True)
        return Response(serializer.data)


class AlbumGenreViewset(CreateListRetrieveViewset):
    permission_classes = (IsAuthenticatedOrReadOnly, )
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
                "mbid": self.kwargs['albums_mbid']}

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


# TODO : adapt with musicbrainz api


class ArtistViewset(ListRetrieveViewset):
    serializer_class = ArtistSerializer
    queryset = Artist.objects.all()
    lookup_field = "mbid"

    def retrieve(self, request, mbid):
        try:
            artist = Artist.objects.get(mbid=mbid)
        except Artist.DoesNotExist:
            artist = create_artist_from_mbid(mbid, 1, "")
        if artist is None:
            return Response({
                "message": "Artist does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance=artist)
        return Response(serializer.data)

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

        # TODO : make a function to scrape discography from musicbrainz
        # allow search by "name" & page number

        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
