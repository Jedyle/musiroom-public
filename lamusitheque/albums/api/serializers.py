from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_recursive.fields import RecursiveField

from albums.models import Genre, Album, Artist, AlbumGenre
from star_ratings.models import UserRating
from star_ratings.api.serializers import RatingSerializer


class GenreSerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="slug",
        queryset=Genre.objects.all(),
        allow_null=True,
    )

    name = serializers.CharField(
        allow_blank=False,
        validators=[UniqueValidator(queryset=Genre.unmoderated_objects.all())],
    )
    children = serializers.ListField(child=RecursiveField(), read_only=True)

    class Meta:
        model = Genre
        fields = ("name", "description", "slug", "parent", "children")
        read_only_fields = ("slug",)
        lookup_field = "slug"


class ShortGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        read_only_fields = ("name", "description", "parent")
        fields = ("slug", "name")


class ArtistListSerializer(serializers.ModelSerializer):

    photo = serializers.CharField(source="get_photo")

    class Meta:
        model = Artist
        fields = ("mbid", "name", "photo")


class AlbumSerializer(serializers.ModelSerializer):
    tracks = serializers.JSONField()
    artists = ArtistListSerializer(many=True)
    cover = serializers.CharField(source="get_cover")
    media_cover = serializers.CharField(source="get_media_cover")
    rating = RatingSerializer()
    real_genres = ShortGenreSerializer(many=True, read_only=True)

    user_rating = serializers.SerializerMethodField()
    followees_avg = serializers.SerializerMethodField()

    class Meta:
        model = Album
        exclude = ("users_interested",)
        lookup_field = "mbid"

    def get_user_rating(self, obj):
        request = self.context.get("request")
        if request and not request.user.is_anonymous:
            user_rating = UserRating.objects.for_instance_by_user(
                obj, user=request.user
            )
            return user_rating.score if user_rating else None

    def get_followees_avg(self, obj):
        request = self.context.get("request")
        if request and not request.user.is_anonymous:
            return obj.rating.followees_ratings_stats(request.user)["average"]


class ShortArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ("mbid", "name", "photo")


class ShortAlbumSerializer(serializers.ModelSerializer):
    """
    Albums serializer with only important data : mbid, and name.
    Used by AlbumGenreSerializer (no need to get the album tracks here for example)
    """

    cover = serializers.SerializerMethodField()
    media_cover = serializers.CharField(source="get_media_cover")

    class Meta:
        model = Album
        fields = ("title", "mbid", "cover", "media_cover")
        read_only_fields = ("title", "mbid", "cover", "media_cover")
        lookup_field = "mbid"

    def get_cover(self, obj):
        return obj.get_cover()


class AlbumGenreSerializer(serializers.ModelSerializer):
    """
    Serializer class for AlbumGenre :
        - album
        - genre
        - number of votes
        - user vote if exists
    """

    album = serializers.SlugRelatedField(slug_field="mbid", read_only=True)
    genre = serializers.SlugRelatedField(
        slug_field="slug", queryset=Genre.objects.all()
    )
    genre_details = serializers.SerializerMethodField(read_only=True)
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    user_vote = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AlbumGenre
        fields = (
            "album",
            "genre",
            "genre_details",
            "user",
            "user_vote",
            "num_vote_up",
            "num_vote_down",
            "vote_score",
            "is_genre",
        )
        read_only_fields = ("num_vote_up", "num_vote_down", "vote_score")

    def get_genre_details(self, obj):
        return ShortGenreSerializer(obj.genre).data

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

    def validate_genre(self, value):
        mbid = self.context.get("mbid")
        duplicate = AlbumGenre.objects.filter(album__mbid=mbid, genre=value).exists()
        if duplicate:
            raise serializers.ValidationError(_("This field must be unique."))
        return value

    def create(self, validated_data):
        genre = validated_data["genre"]
        print(genre)
        mbid = self.context.get("mbid")
        album = get_object_or_404(Album, mbid=mbid)
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        print(genre)
        albumgenre = AlbumGenre(album=album, genre=genre, user=user)
        albumgenre.save()
        if user is not None:
            # user who submitted the genre auto votes
            albumgenre.votes.up(user.id)
        return albumgenre


class ArtistSerializer(serializers.ModelSerializer):

    photo = serializers.CharField(source="get_photo")
    associated_genres = GenreSerializer(source="get_associated_genres", many=True)

    class Meta:
        model = Artist
        exclude = ("albums",)


class UserInterestSerializer(serializers.Serializer):
    value = serializers.BooleanField(required=True)
