from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models
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


#models tests


"""
Tests :
- 
"""


class DiscussionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username = 'Toto', password='12345')
        self.instance = User.objects.create(username = 'Tata', password='23456') #used as a content object for discussions (could be any other model)
    
    def create_discussion(self, author, content_object, title='This is a test', content='Yes, this is a test'):
        return Discussion.objects.create(author = author, content_object= content_object, title = title, content= content)

    def test_discussion_creation(self):
        disc = self.create_discussion(author = self.user, content_object = self.instance)
        self.assertTrue(isinstance(disc, Discussion))
        self.assertEqual(disc.content_object, self.instance)
        self.assertEqual(disc.get_absolute_url(), reverse('discussions:display_discussion', args=[disc.pk]))


class DiscussionViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username = 'Toto', password='12345')
        self.instance = User.objects.create(username = 'Tata', password='23456') #used as a content object for discussions (could be any other model)
        self.discussion = Discussion.objects.create(author = self.user, content_object = self.instance, title = 'Title', content= 'Content')

    def check_status(self, name, args, status, params=""):
        url = reverse(name, args=args) + params
        res = self.client.get(url)
        self.assertEqual(res.status_code, status)

    def test_display_discussion(self):
        self.check_status('discussions:display_discussion', [self.discussion.id], 200)

    def test_display_discussion_404(self):
        self.check_status('discussions:display_discussion', [12], 404)

    def test_search_discussion_for_object_no_args(self):
        self.check_status('discussions:search_discussion_for_object', [], 200)

    def test_search_discussion_for_object_no_args_filters(self):
        self.check_status('discussions:search_discussion_for_object', [], 200, params="?auteur=Toto")
        self.check_status('discussions:search_discussion_for_object', [], 200, params="?auteur=Toti")
        self.check_status('discussions:search_discussion_for_object', [], 200, params="?titre=Title")
        self.check_status('discussions:search_discussion_for_object', [], 200, params="?titre=Titlee")
        self.check_status('discussions:search_discussion_for_object', [], 200, params="?page=toto")
        self.check_status('discussions:search_discussion_for_object', [], 200, params="?page=-1")
        self.check_status('discussions:search_discussion_for_object', [], 200, params="?page=10")
        self.check_status('discussions:search_discussion_for_object', [], 200, params="?filtre=meilleurs")
        self.check_status('discussions:search_discussion_for_object', [], 200, params="?filtre=toto")
        self.check_status('discussions:search_discussion_for_object', [], 200, params="?filtre=récents")
        self.check_status('discussions:search_discussion_for_object', [], 200, params="?filtre=populaires")
        

    def test_search_discussion_for_object_with_args(self):
        ct_pk = self.discussion.content_type.pk
        obj_pk = self.discussion.object_id
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200)

    def test_search_discussion_for_object_with_args_filters(self):
        ct_pk = self.discussion.content_type.pk
        obj_pk = self.discussion.object_id
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200, params="?auteur=Toto")
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200, params="?auteur=Toti")
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200, params="?titre=Title")
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200, params="?titre=Titlee")
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200, params="?page=toto")
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200, params="?page=-1")
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200, params="?page=10")
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200, params="?filtre=meilleurs")
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200, params="?filtre=toto")
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200, params="?filtre=récents")
        self.check_status('discussions:search_discussion_for_object', [ct_pk, obj_pk], 200, params="?filtre=populaires")

    def check_login_status(self, name, args):
        # not logged in
        self.check_status(name, args, 302)
        logged_in = self.client.force_login(self.user)
        # logged in
        self.check_status(name, args, 200)

    def test_create_discussion_login(self):
        self.check_login_status('discussions:create_discussion', [])

    def test_create_discussion_with_args_login(self):
        self.check_login_status('discussions:create_discussion', [self.discussion.content_type.pk, self.discussion.object_id])

    def test_edit_discussion_login(self):
        self.check_login_status('discussions:edit_discussion', [self.discussion.id])
