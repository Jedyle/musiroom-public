from rest_framework import serializers
from albums.models import Album
from reviews.api.simple_serializers import SimpleReviewSerializer
from star_ratings.models import Rating, UserRating
from generic_relations.relations import GenericRelatedField
from user_profile.api.serializers import ShortUserSerializer

class RatingSerializer(serializers.ModelSerializer):

    average = serializers.FloatField(min_value=1, max_value=10)
    
    class Meta:
        model = Rating
        exclude = ("object_id", "content_type")


class UserRatingSerializer(serializers.ModelSerializer):

    review = SimpleReviewSerializer(read_only=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    score = serializers.IntegerField(min_value=1, max_value=10)
    
    class Meta:
        model = UserRating
        exclude = ('ip', )
        read_only_fields = ('rating', 'user')


class ExtendedUserRatingSerializer(serializers.ModelSerializer):

    content_object = serializers.SerializerMethodField()
    user = ShortUserSerializer(read_only=True)
    
    class Meta:
        model = UserRating
        exclude = ('ip', )
        read_only_fields = ('rating', 'user')

    def get_content_object(self, obj):
        # local import to avoid circular import issues
        from albums.api.serializers import AlbumSerializer
        serializers_classes = {
            Album: AlbumSerializer
        }
        ct = obj.rating.content_type
        serializer_class = serializers_classes.get(ct.model_class())
        if serializer_class is None:
            return None
        return serializer_class(obj.rating.content_object).data
