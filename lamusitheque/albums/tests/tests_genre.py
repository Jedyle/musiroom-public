from django.contrib.auth.models import User

from albums.models import Genre
from lamusitheque.apiutils.generic_tests import GenericAPITest

"""
Test permissions
Test post -> moderated
"""


class GenreViewsetTest(GenericAPITest):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username="test", password="testmdp")

        self.genres = [
            Genre.objects.create(name='Rock', description='This is rock!', slug='rock'),
            Genre.objects.create(name="Jazz", description='This is jazz!', slug='jazz')
        ]

        # approve genre in moderation to make it public
        for genre in self.genres:
            genre.moderated_object.approve(by=self.user, reason="Test")

    def list_url(self):
        return '/api/genres/'

    def object_url(self, slug):
        return '/api/genres/{}/'.format(slug)

    def test_cannot_update(self):
        self.check_func_logged(self.update, auth_key=self.user.auth_token.key, id=self.genres[0].slug,
                               data={}, status_code=405)

    def test_cannot_patch(self):
        self.check_func_logged(self.partial_update, auth_key=self.user.auth_token.key, id=self.genres[0].slug,
                               data={}, status_code=405)

    def test_cannot_delete(self):
        self.check_func_logged(self.destroy, auth_key=self.user.auth_token.key, id=self.genres[0].slug,
                               data={}, status_code=405)

    def test_can_list(self):
        self.check_func_not_logged(self.list, status_code=200)

    def test_can_retrieve(self):
        self.check_func_not_logged(self.retrieve, id=self.genres[0].slug, status_code=200)

    def test_cannot_create_if_not_logged(self):
        data = {
            "name": "Folk",
            "description": "Test",
            "slug": "folk"
        }
        self.check_func_not_logged(self.create, id=self.genres[0].slug,
                                   data=data, status_code=401)

    def test_can_create_if_logged(self):
        data = {
            "name": "Folk",
            "description": "Test",
            "slug": "folk",
            "parent": self.genres[1].slug
        }
        self.check_func_logged(self.create, auth_key=self.user.auth_token.key,
                               data=data, status_code=201)


class AlbumGenreViewsetTest(GenericAPITest):

    # TODO : test permissions
    pass
