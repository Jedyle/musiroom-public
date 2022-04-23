import uuid
import factory
import factory.fuzzy


class AlbumFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "albums.Album"

    mbid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    title = factory.fuzzy.FuzzyText(length=20)
    album_type = "LP"


class ArtistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "albums.Artist"

    mbid = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Faker("name")
