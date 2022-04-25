from .factories import AlbumFactory, ArtistFactory


class TestAlbum:
    def test_str(self):
        album = AlbumFactory()
        assert str(album) == album.title

    def test_youtube_link_called(self, mocker):
        fetch_youtube_link = mocker.patch("albums.models.fetch_youtube_link")
        fetch_youtube_link.return_value = "https://youtube.com/fake"
        album = AlbumFactory()
        assert album.get_youtube_link() == "https://youtube.com/fake"
        fetch_youtube_link.assert_called_once_with(album)

    def test_youtube_link_not_called(self, mocker):
        fetch_youtube_link = mocker.patch("albums.models.fetch_youtube_link")
        fetch_youtube_link.return_value = "https://youtube.com/fake"
        album = AlbumFactory(youtube_link="fake")
        assert album.get_youtube_link() == "fake"
        fetch_youtube_link.assert_not_called()


class TestArtist:
    def test_str(self):
        artist = ArtistFactory()
        assert str(artist) == artist.name
