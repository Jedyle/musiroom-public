from .factories import AlbumFactory, ArtistFactory


class TestAlbum:
    def test_str(self):
        artist = ArtistFactory()
        album = AlbumFactory()
        album.artists.add(artist)
        album.save()
        assert str(album) == f"{artist.name} - {album.title}"


class TestArtist:
    def test_str(self):
        artist = ArtistFactory()
        assert str(artist) == artist.name
