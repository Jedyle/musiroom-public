import uuid

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from albums.models import Album
from musiroom.apiutils.generic_tests import GenericAPITest
from .models import Discussion

# Create your tests here.


"""

Taches :
- model Discussion
- formulaire : créer une discussion depuis un album / depuis un artiste
- afficher une discussion (template indépendant du content type) -> url dans l'app discussions
- modifier une discussion (wysiwyg) : reprendre la méthode pour modifier une critique, avec fonctions ajax etc
- supprimer une discussion
- voter sur une discussion
- commenter une discussion (avec 5 threads)
- liste des discussions populaires sur un album / artiste
- sur un album, lister aussi les discussions sur l'auteur, et vice versa sur un artiste
- page 'discussions', avec possibilité de recherche



"""

# models tests


"""
Tests :
- 
"""


class DiscussionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="Toto", password="12345")
        self.instance = User.objects.create(
            username="Tata", password="23456"
        )  # used as a content object for discussions (could be any other model)

    def create_discussion(
        self,
        user,
        content_object,
        title="This is a test",
        content="Yes, this is a test",
    ):
        return Discussion.objects.create(
            user=user, content_object=content_object, title=title, content=content
        )

    def test_discussion_creation(self):
        disc = self.create_discussion(user=self.user, content_object=self.instance)
        self.assertTrue(isinstance(disc, Discussion))
        self.assertEqual(disc.content_object, self.instance)


class DiscussionViewTest(GenericAPITest):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username="Toto", password="12345")

        self.instance = Album.objects.create(
            mbid=str(uuid.uuid4()), title="Test", album_type="SI"
        )
        # used as a content object for discussions (could be any other model)
        self.discussion = Discussion.objects.create(
            user=self.user,
            content_object=self.instance,
            title="Title",
            content="Content",
        )

    def list_discussions(self, params=None):
        if params is None:
            params = {}

        params_as_str = "?" + "&".join([key + "=" + params[key] for key in params])
        return self.client.get("/api/discussions/" + params_as_str)

    def test_list_discussions_status(self):
        res = self.list_discussions()
        self.check_status(res, 200)
