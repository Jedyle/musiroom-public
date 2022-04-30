import factory
from .factories import RatingFactory, UserRatingFactory

from django.db.models.signals import post_save


class TestRating:
    def test_str(self):
        rating = RatingFactory()
        assert str(rating) == str(rating.content_object)

    @factory.django.mute_signals(post_save)
    def test_calculate(self):
        """
        Ensure that calculate method doesn't consider null ratings
        """
        rating = RatingFactory()
        user_ratings = [
            UserRatingFactory(score=5, rating=rating),
            UserRatingFactory(score=2, rating=rating),
            UserRatingFactory(score=5, rating=rating),
            UserRatingFactory(
                rating=rating
            ),  # no score, therefore is means album is just in collection
        ]
        rating.calculate()
        assert rating.average == 4
        assert rating.count == 3  # last rating should not be counter
        assert rating.total == 12
