import datetime
import uuid

from rest_framework.test import APIClient

from albums.models import Album
from lamusitheque.apiutils.generic_tests import GenericAPITest


class AlbumViewsetTest(GenericAPITest):

    def setUp(self):
        self.client = APIClient()

    def list_albums(self):
        return self.client.get('/api/albums/')

    def retrieve_album(self, mbid):
        return self.client.get('/api/albums/' + mbid + '/')

    def test_list_albums(self):
        res = self.list_albums()
        self.check_status(res, 200)

    def test_retrieve_album_in_db(self):
        mbid = str(uuid.uuid4())
        album = Album.objects.create(mbid=mbid,
                                     title="Test",
                                     release_date=datetime.date(2015, 1, 1),
                                     album_type='SI'
                                     )
        res = self.retrieve_album(mbid)
        self.check_status(res, 200)

    def test_retrieve_album_in_musicbrainz(self):
        # this album exists in musicbrainz database
        mbid = "1e8e4ce8-f334-3ec7-af9a-d7babbdb2fd2"
        self.assertFalse(Album.objects.filter(mbid=mbid).exists())
        res = self.retrieve_album(mbid)
        self.check_status(res, 200)
        self.assertTrue(Album.objects.filter(mbid=mbid).exists())

    def test_retrieve_inexistant_album(self):
        # this mbid does not belong to an album in musicbrainz db
        mbid = "1e8e4ce8-f334-3ec7-af9a-d7babbdb2fd3"
        res = self.retrieve_album(mbid)
        self.check_status(res, 404)

    def test_put_request_bad_method(self):
        mbid = str(uuid.uuid4())
        res = self.client.put("/api/albums/" + mbid + "/")
        self.check_status(res, 405)

    def test_post_request_bad_method(self):
        res = self.client.post("/api/albums/")
        self.check_status(res, 405)

    def test_delete_request_bad_method(self):
        mbid = str(uuid.uuid4())
        res = self.client.delete("/api/albums/" + mbid + "/")
        self.check_status(res, 405)

    def test_patch_request_bad_method(self):
        mbid = str(uuid.uuid4())
        res = self.client.patch("/api/albums/" + mbid + "/")
        self.check_status(res, 405)