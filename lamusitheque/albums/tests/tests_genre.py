from django.contrib.auth.models import User
from rest_framework.test import APIClient

from albums.models import Genre
from lamusitheque.apiutils.generic_tests import GenericAPITest


class GenreViewsetTest(GenericAPITest):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username="test", password="testmdp")

        self.genres = [
            Genre.objects.create(name='Rock', description='This is rock!', slug='rock'),
            Genre.objects.create(name="Jazz", description='This is jazz!', slug='jazz')
        ]

        # approve genre in moderation to make it public
        for genre in self.genres:
            genre.moderated_object.approve(by=self.user, reason="Test")

    def list_genres(self):
        return self.client.get('/api/genres/')

    def retrieve_genre(self, slug):
        return self.client.get('/api/genres/' + slug + '/')

    def create_genre(self, data):
        return self.client.post('/api/genres/', data)

    def test_list_genres(self):
        res = self.list_genres()
        self.check_status(res, 200)

    def test_list_genres_length(self):
        res = self.list_genres()
        data = res.data
        self.assertEqual(data["count"], len(self.genres))

    def test_retrieve_genre(self):
        res = self.retrieve_genre(self.genres[0].slug)
        self.check_status(res, 200)


