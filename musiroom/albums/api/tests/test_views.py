import pytest

from rest_framework import status
from albums.models import Album, Artist
from albums.tests.factories import AlbumFactory, ArtistFactory


class TestAlbumListView:

    URL = "/api/albums/"

    def test_list_albums(self, client):
        AlbumFactory.create_batch(5)
        response = client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 5


class TestAlbumRetrieveView:

    URL = "/api/albums/{}/"

    @pytest.mark.api
    def test_album_retrieve_in_db(self, client):
        album = AlbumFactory()
        response = client.get(self.URL.format(album.mbid))
        assert response.status_code == status.HTTP_200_OK
        assert "cover" not in response.json()

    @pytest.mark.api
    def test_album_retrieve_in_musicbrainz(self, client):
        """
        We try to access an album not in the db yet, but in musicbrainz
        """
        mbid = "1e8e4ce8-f334-3ec7-af9a-d7babbdb2fd2"  # Orchid by Opeth
        assert not Album.objects.filter(mbid=mbid).exists()
        response = client.get(self.URL.format(mbid))
        assert response.status_code == status.HTTP_200_OK
        assert "cover" not in response.json()
        album = Album.objects.get(mbid=mbid)  # assert object exists
        assert album.artists.count() == 1  # Opeth

    @pytest.mark.api
    def test_retrieve_inexistant_album(self, client):
        # this mbid does not belong to an album in musicbrainz db
        mbid = "1e8e4ce8-f334-3ec7-af9a-d7babbdb2fd3"
        response = client.get(self.URL.format(mbid))
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAlbumGetYoutubeLinkAction:
    URL = "/api/albums/{}/youtube_link/"

    def test_ok(self, client):
        album = AlbumFactory(youtube_link="fake")
        response = client.get(self.URL.format(album.mbid))
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"link": "fake"}


class TestAlbumGetSpotifyLinkAction:
    URL = "/api/albums/{}/spotify_link/"

    def test_ok(self, client):
        album = AlbumFactory(spotify_link="fake")
        response = client.get(self.URL.format(album.mbid))
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"link": "fake"}


class TestArtistListView:

    URL = "/api/artists/"

    def test_ok(self, client):
        ArtistFactory.create_batch(5)
        response = client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 5


class TestArtistRetrieve:

    URL = "/api/artists/{}/"

    def test_retrieve_in_db(self, client):
        artist = ArtistFactory()
        response = client.get(self.URL.format(artist.mbid))
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.api
    def test_artist_retrieve_in_musicbrainz(self, client):
        """
        We try to access an artist not in the db yet, but in musicbrainz
        """
        mbid = "c14b4180-dc87-481e-b17a-64e4150f90f6"
        assert not Artist.objects.filter(mbid=mbid).exists()
        response = client.get(self.URL.format(mbid))
        assert response.status_code == status.HTTP_200_OK
        assert Artist.objects.filter(mbid=mbid).exists()

    @pytest.mark.api
    def test_retrieve_inexistant_album(self, client):
        # this mbid does not belong to an artist in musicbrainz db
        mbid = "1e8e4ce8-f334-3ec7-af9a-d7babbdb2fd3"
        response = client.get(self.URL.format(mbid))
        assert response.status_code == status.HTTP_404_NOT_FOUND
