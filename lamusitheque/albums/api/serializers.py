from django.shortcuts import get_object_or_404
from rest_framework import serializers

from albums.models import Genre, Album, Artist, AlbumGenre
from star_ratings.api.serializers import RatingSerializer


class GenreSerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(many=False, read_only=False, slug_field="slug", queryset=Genre.objects.all(), allow_null=True)

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
    rating = RatingSerializer()
    genres = serializers.SlugRelatedField(slug_field="slug", read_only=True, many=True)

    class Meta:
        model = Album
        exclude = ('id', 'users_interested')
        lookup_field = "mbid"


class ShortArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ('mbid', 'name')


class ShortAlbumSerializer(serializers.ModelSerializer):
    """
    Albums serializer with only important data : mbid, and name.
    Used by AlbumGenreSerializer (no need to get the album tracks here for example)
    """

    cover = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ('title', 'mbid', 'cover')
        read_only_fields = ('title', 'mbid', 'cover')
        lookup_field = "mbid"

    def get_cover(self, obj):
        return obj.get_cover()


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
        mbid = self.context.get("mbid")
        album = get_object_or_404(Album, mbid=mbid)
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


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        exclude = ("albums",)


class UserInterestSerializer(serializers.Serializer):
    value = serializers.ChoiceField(required=True, choices=[False, True])
