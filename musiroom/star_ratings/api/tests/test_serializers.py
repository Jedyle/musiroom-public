import pytest
from rest_framework import serializers
from star_ratings.api.serializers import UserRatingSerializer


class TestUserRatingSerializer:
    def test_nothing_set(self):
        serializer = UserRatingSerializer(
            data={"score": None, "is_interested": False, "is_in_collection": False}
        )
        with pytest.raises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_rating_but_no_collection(self):
        serializer = UserRatingSerializer(
            data={"score": 8, "is_interested": False, "is_in_collection": False}
        )
        with pytest.raises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_rate(self):
        serializer = UserRatingSerializer(
            data={"score": 8, "is_interested": False, "is_in_collection": True}
        )
        serializer.is_valid(raise_exception=True)

    def test_to_collection(self):
        serializer = UserRatingSerializer(
            data={"score": None, "is_interested": False, "is_in_collection": True}
        )
        serializer.is_valid(raise_exception=True)

    def test_interested(self):
        serializer = UserRatingSerializer(
            data={"score": None, "is_interested": True, "is_in_collection": False}
        )
        serializer.is_valid(raise_exception=True)
