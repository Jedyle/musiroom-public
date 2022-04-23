import pytest
from .factories import AlbumFactory, ArtistFactory


class TestAlbum:
    def test_str(self):
        album = AlbumFactory()
        assert str(album) == album.title


class TestArtist:
    def test_str(self):
        artist = ArtistFactory()
        assert str(artist) == artist.name
