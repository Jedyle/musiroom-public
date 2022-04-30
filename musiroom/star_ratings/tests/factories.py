import factory
from albums.tests.factories import AlbumFactory
from star_ratings.models import Rating, UserRating


class RatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rating

    content_object = factory.SubFactory(AlbumFactory)


class UserRatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserRating

    rating = factory.SubFactory(RatingFactory)
