import requests
import os
import re

from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.templatetags.static import static
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.db.models import Count, Q
from django.http import Http404
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from siteflags.models import ModelWithFlag
from vote.models import VoteModel
from django.db.utils import DataError

from albums.utils import load_album_if_not_exists, create_artist_from_mbid
from albums.scrapers.spotify import MBToSpotify
from albums.scrapers.deezer import MBToDeezer
from albums.scrapers.youtube import fetch_youtube_link
from discussions.register import discussions_registry
from star_ratings.models import Rating
from .scraper import PROTOCOL, COVER_URL, ParseArtistPhoto

# Create your models here.


class GenreManager(models.Manager):
    def generate_tree(self):
        roots = self.filter(parent__isnull=True)
        genre_tree = [
            {
                "name": root.name,
                "slug": root.slug,
                "url": reverse("albums:genre", args=[root.slug]),
            }
            for root in roots
        ]
        for i in range(len(genre_tree)):
            self.gen_child_tree(genre_tree[i])
        return {"tree": genre_tree}

    def gen_child_tree(self, genre_dict):
        slug = genre_dict["slug"]
        genre = Genre.objects.get(slug=slug)
        children = genre.children
        children_tree = [
            {
                "name": child.name,
                "slug": child.slug,
                "url": reverse("albums:genre", args=[child.slug]),
            }
            for child in children
        ]
        if len(children_tree) > 0:
            genre_dict["children"] = children_tree
            for i in range(len(children_tree)):
                self.gen_child_tree(children_tree[i])


class Genre(models.Model):
    name = models.CharField("Name", max_length=200, help_text="Genre name", unique=True)
    description = models.TextField(
        "Description",
        blank=True,
        null=True,
        default="",
        help_text="Description du genre",
    )
    slug = models.SlugField(
        "Slug",
        max_length=255,
        db_index=True,
        null=False,
        unique=True,
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
        if not self.slug:
            self.slug = slugify(self.name)
        super(Genre, self).save(*args, **kwargs)

    @property
    def children(self):
        return self.genre_set.all().order_by("name")


SLUG_ALL_VALUE = "all"
YEAR_ALL_VALUE = "all"


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

    def get_top(self, year, slug):
        albums = self.all()
        if year != YEAR_ALL_VALUE:
            m = re.match(r"^([0-9]{4})s$", year)
            if m is not None:
                decade = int(m.group(1))
                years = [(decade + i) for i in range(10)]
            else:
                years = [int(year)]
            albums = albums.filter(release_date__year__in=years)

        if slug != SLUG_ALL_VALUE:
            genre = get_object_or_404(Genre, slug=slug)
            associated_genres = genre.get_all_children()
            albums = albums.filter(
                Q(albumgenre__genre__in=associated_genres)
                & Q(albumgenre__is_genre=True)
            )

        albums = albums.filter(
            Q(ratings__isnull=False)
            & Q(ratings__average__gt=1.0)
            & Q(ratings__count__gt=2)
        ).order_by("-ratings__average", "title")

        albums = albums.distinct().prefetch_related("artists")[:100]
        return albums


class Album(models.Model):
    mbid = models.CharField(db_index=True, max_length=36, unique=True)
    title = models.CharField(max_length=500, db_index=True)
    release_date = models.DateField(blank=True, null=True)
    cover = models.CharField(max_length=100, null=True)
    # same as cover, but the actual image stored in our system (for more speed)
    media_cover = models.ImageField(upload_to="album_covers", null=True)
    tracks = models.JSONField(null=True)

    TYPE_CHOICES = (
        ("SI", "Single"),
        ("LP", "LP"),
        ("EP", "EP"),
        ("LI", "Live"),
        ("CP", "Compilation"),
        ("RE", "Remix"),
        ("UK", "Unknown"),
    )

    album_type = models.CharField(max_length=2, choices=TYPE_CHOICES, default="LP")
    genres = models.ManyToManyField(
        Genre,
        related_name="albums",
        blank=True,
        through="AlbumGenre",
        through_fields=("album", "genre"),
    )

    ratings = GenericRelation(Rating, related_query_name="albums")

    objects = AlbumManager()

    def save(self, *args, **kwargs):
        if not self.media_cover and self.cover:
            response = requests.get(PROTOCOL + COVER_URL + "release/" + self.cover)
            if response.ok:
                tmp_file = NamedTemporaryFile()
                tmp_file.write(response.content)
                tmp_file.flush()
                img = File(tmp_file)
                self.media_cover.save(os.path.basename(self.cover), img)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.artists.exists():
            return f"{self.artists.first().name} - {self.title}"
        return self.title

    def verbose_name(self):
        if self.album_type == "UK":
            return self.title
        return "{} ({})".format(self.title, self.get_album_type_display())

    def get_absolute_url(self):
        return reverse("album-detail", args=[self.mbid])

    def get_release_date(self):
        if self.release_date is None:
            return ""
        elif self.release_date.month == 12 and self.release_date.day == 31:
            return self.release_date.year
        else:
            return self.release_date

    def get_cover(self):
        if self.cover:
            return PROTOCOL + COVER_URL + "release/" + self.cover
        return settings.BACKEND_URL + static("albums/images/default_cover.png")

    def get_media_cover(self):
        cover = (
            self.media_cover.url
            if self.media_cover
            else static("albums/images/default_cover.png")
        )
        return settings.BACKEND_URL + cover

    def get_preview(self):
        return self.get_cover()

    class Meta:
        verbose_name = "Album"
        ordering = ("pk",)

    @property
    def rating(self):
        # for drf, property to add nested serializer
        return Rating.objects.for_instance(self)

    @property
    def real_genres(self):
        return self.genres.filter(albumgenre__is_genre=True).order_by(
            "albumgenre__vote_score"
        )

    def activity_data(self):
        return {"mbid": self.mbid}


discussions_registry.register(Album)


class AlbumLinks(models.Model):
    album = models.OneToOneField(Album, on_delete=models.CASCADE, related_name="links")
    youtube = models.CharField(max_length=200, null=True)
    spotify = models.CharField(max_length=200, null=True)
    deezer = models.CharField(max_length=200, null=True)

    def _get_or_create_field(self, field, create_field_function):
        if getattr(self, field):
            return getattr(self, field)
        else:
            setattr(self, field, create_field_function(self.album))
            self.save()
            return getattr(self, field)

    def get_youtube(self):
        return self._get_or_create_field("youtube", fetch_youtube_link)

    def get_spotify(self):
        return self._get_or_create_field(
            "spotify", lambda album: MBToSpotify().find_album(album.mbid)
        )

    def get_deezer(self):
        return self._get_or_create_field(
            "deezer", lambda album: MBToDeezer().find_album(album.mbid)
        )

    def reset(self):
        """
        Call this function to regenerate the links
        They will be set to None, hence get_xxx will redo the API call
        """
        self.spotify = None
        self.youtube = None
        self.save()


class AlbumGenre(VoteModel, ModelWithFlag, models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    is_genre = models.BooleanField(
        default=False
    )  # true if this genre is registered as one of the album's genre

    FLAG_SPAM = 10

    def __str__(self):
        return "%s - %s" % (self.album.title, self.genre.name)

    def get_absolute_url(self):
        return reverse("genres-detail", args=[self.album.mbid, self.genre.slug])

    class Meta:
        unique_together = ("album", "genre")


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
    mbid = models.CharField(
        db_index=True,
        max_length=36,
        unique=True,
        validators=[MinLengthValidator(36), MaxLengthValidator(36)],
    )
    name = models.CharField(max_length=100, db_index=True)
    albums = models.ManyToManyField(Album, related_name="artists", blank=True)
    photo = models.CharField(max_length=300, null=True)

    objects = ArtistManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("artist-detail", args=[self.mbid])

    def get_photo(self):
        default_photo_url = settings.BACKEND_URL + static("images/artist.jpg")
        if self.photo is None:
            parser = ParseArtistPhoto(self.mbid)
            if parser.load():
                photo = parser.get_thumb()
                self.photo = photo
                try:
                    self.save()
                except django.db.utils.DataError as e:
                    # if photo url is too long, fail silently
                    # TODO : rename photo instead
                    print(e)
                    self.photo = ""
                    self.save()
                if photo != "":
                    return photo
                return default_photo_url
        elif self.photo == "":
            return default_photo_url
        return self.photo

    def get_preview(self):
        return self.get_photo()

    def get_associated_genres(self):
        return (
            Genre.objects.filter(
                albumgenre__album__artists__in=[self], albumgenre__is_genre=True
            )
            .annotate(total=Count("id"))
            .order_by("-total")[:3]
        )

    class Meta:
        verbose_name = "Artiste"


discussions_registry.register(Artist)
