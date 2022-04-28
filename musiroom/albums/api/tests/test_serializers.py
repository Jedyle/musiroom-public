from albums.tests.factories import AlbumFactory
from albums.api.serializers import AlbumSerializer


class TestSerializer:

    def test_ok(self):
        album = AlbumFactory(album_type="UK")
        serializer = AlbumSerializer(instance=album)
        assert serializer.data["album_type"] == "Unknown"
