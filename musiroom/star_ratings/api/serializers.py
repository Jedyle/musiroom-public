from rest_framework import serializers
from albums.models import Album
from reviews.models import Review
from reviews.api.simple_serializers import SimpleReviewSerializer
from star_ratings.models import Rating, UserRating
from user_profile.api.short_serializers import ShortUserSerializer


class RatingSerializer(serializers.ModelSerializer):

    average = serializers.FloatField(min_value=1, max_value=10)

    class Meta:
        model = Rating
        exclude = ("object_id", "content_type")


class ShortUserRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRating
        fields = ("score", "is_interested", "is_in_collection")


class UserRatingSerializer(serializers.ModelSerializer):

    review = SimpleReviewSerializer(read_only=True)
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    score = serializers.IntegerField(allow_null=True, min_value=1, max_value=10)

    class Meta:
        model = UserRating
        fields = (
            "id",
            "review",
            "user",
            "score",
            "is_interested",
            "is_in_collection",
            "rating",
        )
        read_only_fields = ("rating", "user")

    def validate(self, data):
        score = data.get("score")
        is_interested = data.get("is_interested", False)
        is_in_collection = data.get("is_in_collection", True)
        if (score is not None) and (is_in_collection is False):
            raise serializers.ValidationError(
                "Must set is_in_collection to True if rating is not null"
            )
        if (score is None) and (is_in_collection is False) and (is_interested is False):
            raise serializers.ValidationError(
                "No field amoung score, is_in_collection and is_interested is set. Delete the rating is that case !"
            )
        return data

    def update(self, instance, validated_data):
        print(validated_data)
        if (
            validated_data.get("score") is None
            and Review.objects.filter(rating=instance).exists()
        ):
            Review.objects.filter(rating=instance).delete()
        instance.save()
        return super().update(instance, validated_data)


class ExtendedUserRatingSerializer(serializers.ModelSerializer):

    content_object = serializers.SerializerMethodField()
    user = ShortUserSerializer(read_only=True)

    class Meta:
        model = UserRating
        fields = (
            "id",
            "content_object",
            "user",
            "rating",
            "score",
            "is_interested",
            "is_in_collection",
            "modified",
            "created",
        )
        read_only_fields = ("rating", "user")

    def get_content_object(self, obj):
        # local import to avoid circular import issues
        from albums.api.serializers import AlbumSerializer

        serializers_classes = {Album: AlbumSerializer}
        ct = obj.rating.content_type
        serializer_class = serializers_classes.get(ct.model_class())
        if serializer_class is None:
            return None
        return serializer_class(obj.rating.content_object).data
