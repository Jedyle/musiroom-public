from django.db import models
from django.contrib.auth.models import User
from vote.models import VoteModel
from siteflags.models import ModelWithFlag
from .scraper import PROTOCOL, COVER_URL, ARTIST, ALBUM
import datetime
from django.db.models.signals import post_save
from star_ratings.models import Rating
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.dispatch import receiver


# Create your models here.

class Genre(models.Model):
    name = models.CharField('Nom',
        max_length=200,
        help_text="Nom du genre",
        unique = True,
    )
    description = models.TextField('Description',
        blank=True,
        null=True,
        default="",
        help_text="Description du genre",
    )
    slug = models.SlugField('Slug',
        max_length=255,
        db_index=True,
        null=True,
        unique=True,
        help_text="Court nom descriptif pour les urls",
    )
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE
    )

    def __unicode__(self):
        return self.name

    __str__ = __unicode__

    class Meta:
        ordering = ("name",)
        verbose_name = "genre"
        verbose_name_plural = "genres"

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


class Album(models.Model):
    mbid = models.CharField(db_index=True,max_length = 36, unique = True)
    title = models.CharField(max_length = 100)
    release_date = models.DateField(blank = True, null = True)
    cover = models.CharField(max_length = 100, null = True)

    TYPE_CHOICES = (
        ('SI', 'Single'),
        ('LP' , 'Album'),
        ('EP' , 'EP'),
        ('LI' , 'Live'),
        ('CP' , 'Compilation'),
        ('RE' , 'Remix'),
        ('UK', 'Inconnu'),
        )
    
    album_type = models.CharField(max_length = 2, choices = TYPE_CHOICES, default='LP')
    genres = models.ManyToManyField(Genre, related_name='albums', blank = True, through= 'AlbumGenre', through_fields=('album', 'genre'))

    ratings = GenericRelation(Rating, related_query_name='albums')

    def __str__(self):
        return self.title
        
    def get_release_date(self):
        if self.release_date is None:
            return ""
        elif self.release_date.month == 12 and self.release_date.day == 31:
            return self.release_date.year
        else:
            return self.release_date

    def get_cover(self):
        if self.cover:
            return PROTOCOL + COVER_URL + '/release/' + self.cover
        return static('albums/images/default_cover.png')

    class Meta:
        verbose_name = "Album"


class AlbumGenre(VoteModel, ModelWithFlag, models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    is_genre = models.BooleanField(default = False) #true if this genre is registered as one of the album's genre

    FLAG_SPAM = 10

    def __str__(self):
        return "%s - %s" % (self.album.title, self.genre.name)

class Artist(models.Model):
    mbid = models.CharField(db_index=True, max_length = 36, unique = True)
    name = models.CharField(max_length = 50)
    albums = models.ManyToManyField(Album, related_name='artists', blank = True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Artiste"
        
    
@receiver(post_save, sender=AlbumGenre)
def update_genres_handler(sender, instance, **kwargs):
    album = instance.album
    genres = AlbumGenre.objects.filter(album = album, vote_score__gt=0).order_by('-vote_score')
    registered_genres = genres[:3]
    AlbumGenre.objects.filter(id__in=registered_genres).update(is_genre = True)
    AlbumGenre.objects.filter(album = album).exclude(id__in=registered_genres).update(is_genre = False)    
