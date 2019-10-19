import datetime
import uuid

from albums.models import Album
from lamusitheque.apiutils.generic_tests import GenericAPITest


class AlbumViewsetTest(GenericAPITest):

    def object_url(self, id):
        return "/api/albums/{}/".format(id)

    def list_url(self):
        return "/api/albums/"

    def test_list_albums(self):
        res = self.list()
        self.check_status(res, 200)

    def test_retrieve_album_in_db(self):
        mbid = str(uuid.uuid4())
        album = Album.objects.create(mbid=mbid,
                                     title="Test",
                                     release_date=datetime.date(2015, 1, 1),
                                     album_type='SI'
                                     )
        res = self.retrieve(mbid)
        self.check_status(res, 200)

    def test_retrieve_album_in_musicbrainz(self):
        # this album exists in musicbrainz database
        mbid = "1e8e4ce8-f334-3ec7-af9a-d7babbdb2fd2"
        self.assertFalse(Album.objects.filter(mbid=mbid).exists())
        res = self.retrieve(mbid)
        self.check_status(res, 200)
        self.assertTrue(Album.objects.filter(mbid=mbid).exists())

    def test_retrieve_inexistant_album(self):
        # this mbid does not belong to an album in musicbrainz db
        mbid = "1e8e4ce8-f334-3ec7-af9a-d7babbdb2fd3"
        res = self.retrieve(mbid)
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

    def test_get_user_interest_not_logged(self):
        res = self.client.get(self.object_url(str(uuid.uuid4())) + 'user_interest/')
        self.check_status(res, 401)

    def test_put_user_interest_not_logged(self):
        res = self.client.put(self.object_url(str(uuid.uuid4())) + 'user_interest/', data={})
        self.check_status(res, 401)
