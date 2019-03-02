from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models
from django.http import Http404
from django.urls import reverse
from django.utils.functional import cached_property
from jsonfield.fields import JSONField
from siteflags.models import ModelWithFlag
from vote.models import VoteModel

from albums.utils import load_album_if_not_exists, create_artist_from_mbid
from discussions.register import discussions_registry
from star_ratings.models import Rating
from .scraper import PROTOCOL, COVER_URL, ParseArtistPhoto


# Create your models here.

class GenreManager(models.Manager):
    def generate_tree(self):
        roots = self.filter(parent__isnull=True)
        genre_tree = [{'name': root.name, 'slug': root.slug, 'url': reverse('albums:genre', args=[root.slug])} for root
                      in roots]
        for i in range(len(genre_tree)):
            self.gen_child_tree(genre_tree[i])
        return {'tree': genre_tree}

    def gen_child_tree(self, genre_dict):
        slug = genre_dict['slug']
        genre = Genre.objects.get(slug=slug)
        children = genre.children
        children_tree = [{'name': child.name, 'slug': child.slug, 'url': reverse('albums:genre', args=[child.slug])} for
                         child in children]
        if len(children_tree) > 0:
            genre_dict['children'] = children_tree
            for i in range(len(children_tree)):
                self.gen_child_tree(children_tree[i])


class Genre(models.Model):
    name = models.CharField('Name', max_length=200, help_text="Genre name", unique=True)
    description = models.TextField('Description', blank=True, null=True, default="", help_text="Description du genre")
    slug = models.SlugField('Slug', max_length=255, db_index=True, null=False, unique=True,
                            help_text="Slug for urls",
                            )
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    objects = GenreManager()

    def __unicode__(self):
        return self.name

    __str__ = __unicode__

    class Meta:
        ordering = ("name",)
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

    def get_all_children(self):
        children = self.children
        children_list = [self]
        if children.count() > 0:
            for child in children:
                children_list.extend(child.get_all_children())
        return children_list

    def save(self, *args, **kwargs):
        # Raise on circular reference
        parent = self.parent
        while parent is not None:
            if parent == self:
                raise RuntimeError("Références circulaires non autorisées")
            parent = parent.parent
        super(Genre, self).save(*args, **kwargs)

    @property
    def children(self):
        return self.genre_set.all().order_by("name")

    @property
    def api_lookup_value(self):
        return self.slug


class AlbumManager(models.Manager):

    def get_from_api(self, mbid):
        """
        Tries to get album from database, else tries from musicbrainz
        """
        try:
            album = self.get(mbid=mbid)
        except Album.DoesNotExist:
            album, artists = load_album_if_not_exists(mbid)
        if album is None:
            raise Http404
        return album


class Album(models.Model):
    mbid = models.CharField(db_index=True, max_length=36, unique=True)
    title = models.CharField(max_length=500)
    release_date = models.DateField(blank=True, null=True)
    cover = models.CharField(max_length=100, null=True)
    tracks = JSONField(null=True)

    TYPE_CHOICES = (
        ('SI', 'Single'),
        ('LP', 'LP'),
        ('EP', 'EP'),
        ('LI', 'Live'),
        ('CP', 'Compilation'),
        ('RE', 'Remix'),
        ('UK', 'Inconnu'),
    )

    album_type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='LP')
    genres = models.ManyToManyField(Genre, related_name='albums', blank=True, through='AlbumGenre',
                                    through_fields=('album', 'genre'))

    ratings = GenericRelation(Rating, related_query_name='albums')

    users_interested = models.ManyToManyField(User, related_name='interests', blank=True, through='UserInterest',
                                              through_fields=('album', 'user'))

    objects = AlbumManager()

    def __str__(self):
        return self.title

    def verbose_name(self):
        if self.album_type == 'UK':
            return self.title
        return "{} ({})".format(self.title, self.get_album_type_display())

    @property
    def api_lookup_value(self):
        return self.mbid

    @cached_property
    def very_verbose_name(self):
        if self.album_type == 'UK':
            return self.title + ' de ' + ', '.join(str(item) for item in self.artists.all())
        return self.title + ' (' + self.get_album_type_display() + ') de ' + ', '.join(
            str(item) for item in self.artists.all())

    def get_absolute_url(self):
        return reverse('album-detail', args=[self.mbid])

    def get_release_date(self):
        if self.release_date is None:
            return ""
        elif self.release_date.month == 12 and self.release_date.day == 31:
            return self.release_date.year
        else:
            return self.release_date

    def get_cover(self):
        if self.cover:
            return PROTOCOL + COVER_URL + 'release/' + self.cover
        return static('albums/images/default_cover.png')

    def get_preview(self):
        return self.get_cover()

    class Meta:
        verbose_name = "Album"

    @property
    def rating(self):
        # for drf, property to add nested serializer
        return self.ratings.get()


discussions_registry.register(Album)


class AlbumGenre(VoteModel, ModelWithFlag, models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    is_genre = models.BooleanField(default=False)  # true if this genre is registered as one of the album's genre

    FLAG_SPAM = 10

    def __str__(self):
        return "%s - %s" % (self.album.title, self.genre.name)

    def get_absolute_url(self):
        return reverse('genres-detail', args=[self.album.mbid, self.genre.slug])

    class Meta:
        unique_together = ('album', 'genre')


class UserInterest(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField('Creation date', auto_now=True)

    def __str__(self):
        return "%s wants to listen to %s " % (self.user.username, self.album.title)

    class Meta:
        unique_together = ('album', 'user')


class ArtistManager(models.Manager):

    def get_from_api(self, mbid):
        try:
            artist = self.get(mbid=mbid)
        except Artist.DoesNotExist:
            artist = create_artist_from_mbid(mbid, 1, "")
        if artist is None:
            raise Artist.DoesNotExist
        return artist


class Artist(models.Model):
    mbid = models.CharField(db_index=True, max_length=36, unique=True)
    name = models.CharField(max_length=100)
    albums = models.ManyToManyField(Album, related_name='artists', blank=True)
    photo = models.CharField(max_length=150, null=True)

    objects = ArtistManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('artist-detail', args=[self.mbid])

    def get_photo(self):
        if self.photo is None:
            parser = ParseArtistPhoto(self.mbid)
            if parser.load():
                photo = parser.get_thumb()
                self.photo = photo
                self.save()
                if photo != "":
                    return photo
        elif self.photo == "":
            return static('images/artist.jpg')
        return self.photo

    def get_preview(self):
        return self.get_photo()

    @property
    def api_lookup_value(self):
        """
        Get value to lookup in details route in API
        TODO : add this to every model
        :return:
        """
        return self.mbid

    class Meta:
        verbose_name = "Artiste"


discussions_registry.register(Artist)


