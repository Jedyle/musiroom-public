from rest_framework import serializers

from ratings.models import Review


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = "__all__"
        # rating is read_only
        read_only_fields = ('vote_score', 'num_vote_up', 'num_vote_down', 'rating')


class ReviewCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = "__all__"
        # rating is writable
        read_only_fields = ('vote_score', 'num_vote_up', 'num_vote_down')

