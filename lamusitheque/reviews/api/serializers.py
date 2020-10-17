from rest_framework import serializers
from star_ratings.models import UserRating
from reviews.models import Review
from star_ratings.api.serializers import ExtendedUserRatingSerializer
from lamusitheque.apiutils.mixins import VoteSerializerMixin


class ReviewSerializer(serializers.ModelSerializer, VoteSerializerMixin):

    rating = ExtendedUserRatingSerializer(read_only=True)

    class Meta:
        model = Review
        fields = "__all__"
        # rating is read_only
        read_only_fields = ("vote_score", "num_vote_up", "num_vote_down", "rating")


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        # rating is writable
        read_only_fields = ("vote_score", "num_vote_up", "num_vote_down")
