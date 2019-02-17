from django.http import Http404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from albums.models import Genre, Album, Artist, AlbumGenre


class GenreSerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(many=False, read_only=False, slug_field="slug",
                                          queryset=Genre.objects.all(), allow_null=True)

    class Meta:
        model = Genre
        fields = ("name", "description", "slug", "parent")
        lookup_field = 'slug'


class ArtistListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ('mbid', 'name', 'photo')


class AlbumSerializer(serializers.ModelSerializer):
    tracks = serializers.JSONField()
    artists = ArtistListSerializer(many=True)
    cover = serializers.CharField(source='get_cover')

    class Meta:
        model = Album
        exclude = ('id',)
        lookup_field = "mbid"


class ShortAlbumSerializer(serializers.ModelSerializer):
    """
    Albums serializer with only important data : mbid, and name.
    Used by AlbumGenreSerializer (no need to get the album tracks here for example)
    """

    class Meta:
        model = Album
        fields = ('title', 'mbid')
        read_only_fields = ('title', 'mbid')
        lookup_field = "mbid"


class ShortGenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        read_only_fields = ("name", "description", "parent")
        fields = ('slug',)


class AlbumGenreSerializer(serializers.ModelSerializer):
    """
    Serializer class for AlbumGenre :
        - album
        - genre
        - number of votes
        - user vote if exists
    """

    album = serializers.SlugRelatedField(slug_field='mbid', read_only=True)
    genre = serializers.SlugRelatedField(slug_field='slug', queryset=Genre.objects.all())
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    user_vote = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AlbumGenre
        fields = ('album', 'genre', 'user', 'user_vote', 'num_vote_up', 'num_vote_down', 'vote_score')
        read_only_fields = ('num_vote_up', 'num_vote_down', 'vote_score')

    def get_user_vote(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            if obj.votes.exists(user.id, action=0):
                return "up"
            elif obj.votes.exists(user.id, action=1):
                return "down"
        return None

    def create(self, validated_data):
        genre = validated_data['genre']
        try:
            album = Album.objects.get(mbid=self.context.get("mbid"))
        except Album.DoesNotExist:
            raise Http404("This album does not exist")
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        albumgenre = AlbumGenre(album=album, genre=genre, user=user)
        albumgenre.save()
        if user is not None:
            # user who submitted the genre auto votes
            albumgenre.votes.up(user.id)
        return albumgenre


class VoteSerializer(serializers.Serializer):
    vote = serializers.ChoiceField(["up", "down", "null"])


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        exclude = ("albums",)
