import uuid

from rest_framework.test import APIClient

from albums.models import Artist
from lamusitheque.apiutils.generic_tests import GenericAPITest


class ArtistViewsetTest(GenericAPITest):

    def list_artists(self):
        return self.client.get('/api/artists/')

    def retrieve_artist(self, mbid):
        return self.client.get('/api/artists/' + mbid + '/')

    def similar_artists(self, mbid):
        return self.client.get('/api/artists/' + mbid + '/similar/')

    def discography(self, mbid):
        return self.client.get('/api/artists/' + mbid + '/discography/')

    def test_list_artists(self):
        res = self.list_artists()
        self.check_status(res, 200)

    def test_retrieve_artist_in_db(self):
        mbid = str(uuid.uuid4())
        artist = Artist.objects.create(mbid=mbid,
                                       name="Test")
        res = self.retrieve_artist(mbid)
        self.check_status(res, 200)

    def test_retrieve_artist_in_musicbrainz(self):
        # this artist exists in musicbrainz database
        mbid = "c14b4180-dc87-481e-b17a-64e4150f90f6"
        self.assertFalse(Artist.objects.filter(mbid=mbid).exists())
        res = self.retrieve_artist(mbid)
        self.check_status(res, 200)
        self.assertTrue(Artist.objects.filter(mbid=mbid).exists())

    def test_retrieve_inexistant_artist(self):
        # this mbid does not belong to an artist in musicbrainz db
        mbid = "1e8e4ce8-f334-3ec7-af9a-d7babbdb2fd3"
        res = self.retrieve_artist(mbid)
        self.check_status(res, 404)

    def test_put_request_bad_method(self):
        mbid = str(uuid.uuid4())
        res = self.client.put("/api/artists/" + mbid + "/")
        self.check_status(res, 405)

    def test_post_request_bad_method(self):
        res = self.client.post("/api/artists/")
        self.check_status(res, 405)

    def test_delete_request_bad_method(self):
        mbid = str(uuid.uuid4())
        res = self.client.delete("/api/artists/" + mbid + "/")
        self.check_status(res, 405)

    def test_patch_request_bad_method(self):
        mbid = str(uuid.uuid4())
        res = self.client.patch("/api/artists/" + mbid + "/")
        self.check_status(res, 405)
