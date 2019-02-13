from django.test import TestCase
from django.urls import reverse

from .models import *

# Create your tests here.


"""
- album -> crée un album si il n'existe pas, le récupère si il existe
- album -> si le mbid n'existe pas, une page 404 est affichée, sinon une page d'album est affichée
- album -> un artiste est bien créé quand il n'existe pas encore
"""

"""
ATTENTION : TEST DEBUG A FAIRE.
Lorsqu'on fait une recherche d'album et qu'un album a plus d'un artiste, il n'y qu'un lien qui pointe vers le premier artiste

ex : Cult of Luna & Julie Christmas, le lien ne pointe que vers CoL
"""


class AlbumViewTest(TestCase):

    # chaque user créé a un account, et les deux sont liés

    def setUp(self):
        album = Album.objects.create(mbid='f5093c06-23e3-404f-aeaa-40f72885ee3a',
                                     title='The Dark Side of the Moon')  # DSOTM
        artist = Artist.objects.create(mbid='83d91898-7763-47d7-b03b-b92132375c47', name='Pink Floyd')  # Pink Floyd
        artist.albums.add(album)

    def test_404_if_not_album(self):
        response = self.client.get(
            reverse('albums:album', args=['c14b4180-dc87-481e-b17a-64e4150f90f6']))  # id for an artist
        self.assertEqual(response.status_code, 404)

    def test_404_if_not_exists(self):
        response = self.client.get(
            reverse('albums:album', args=['c14b4180-dc87-481e-b17a-64e4150f90f7']))  # does not exist
        self.assertEqual(response.status_code, 404)

    def test_200_if_exists(self):
        response = self.client.get(reverse('albums:album', args=['2864ec02-5e6a-36d8-9960-ccd959b9a618']))  # real album
        self.assertEqual(response.status_code, 200)

    def test_create_if_not_exists(self):
        response = self.client.get(
            reverse('albums:album', args=['4e98c9b4-92f6-3049-b9da-a1088b623672']))  # Meddle by Pink Floyd
        self.assertTrue(Album.objects.filter(mbid='4e98c9b4-92f6-3049-b9da-a1088b623672').exists()
                        and response.status_code == 200)

    def test_create_only_once(self):
        response = self.client.get(reverse('albums:album', args=['f5093c06-23e3-404f-aeaa-40f72885ee3a']))  # DSOTM
        self.assertTrue(
            len(Album.objects.filter(mbid='f5093c06-23e3-404f-aeaa-40f72885ee3a')) == 1 and response.status_code == 200)

    def test_create_artist_if_not_exists(self):
        response = self.client.get(reverse('albums:album', args=['9162580e-5df4-32de-80cc-f45a8d8a9b1d']))
        self.assertTrue(Artist.objects.filter(
            mbid='b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d').exists())  # check if the artist was created


"""
- artist -> si mbid n'existe pas, 404, sinon page d'artiste
- artist -> tous les artistes ont un mbid unique non nul
"""


class ArtistViewTest(TestCase):

    # chaque user créé a un account, et les deux sont liés

    def setUp(self):
        album = Album.objects.create(mbid='f5093c06-23e3-404f-aeaa-40f72885ee3a',
                                     title='The Dark Side of the Moon')  # DSOTM
        artist = Artist.objects.create(mbid='83d91898-7763-47d7-b03b-b92132375c47', name='Pink Floyd')  # Pink Floyd
        artist.albums.add(album)

    def test_404_if_not_artist(self):
        response = self.client.get(
            reverse('albums:artist', args=['4ac65c55-08ac-3855-809e-07e7f4579a68']))  # id for an artist
        self.assertEqual(response.status_code, 404)

    def test_404_if_not_exists(self):
        response = self.client.get(
            reverse('albums:artist', args=['4ac65c55-08ac-3855-809e-07e7f4579a69']))  # does not exist
        self.assertEqual(response.status_code, 404)

    def test_200_if_exists(self):
        response = self.client.get(
            reverse('albums:artist', args=['8ca01f46-53ac-4af2-8516-55a909c0905e']))  # real artist
        self.assertEqual(response.status_code, 200)


"""
- search -> toujours autant de pages sur le site que sur musicbrainz
- get artist in db -> len(retour) == len(arg)

- album_genres : unicité pour un album et un genre

- ajax_vote : on ne peut voter que connecté
- ajax_vote : si l'album n'existe pas (encore) dans la base, ou le genre n'existe pas, 404

- genre : slug unique

- submit_genre : un genre dont le nom existe déjà ne peut pas être soumis. Idem pour slug
- submit_genre : un genre soumis n'est pas visible tant que la modération ne l'a pas acceptée

- scraper
"""
