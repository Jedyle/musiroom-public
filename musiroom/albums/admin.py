from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from siteflags.utils import get_flag_model

from moderation.admin import ModerationAdmin
from .models import Album, Artist, Genre


# TODO : ModerationAdmin blocks migrations when creating a new database ! Fix this.

# Register your models here.


class GenreParentFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "parent"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "parent"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        parents = set([genre.parent for genre in model_admin.model.objects.all()])
        return [("none", "None")] + [
            (genre.slug, genre.name) for genre in parents if genre is not None
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == "none":
            return queryset.filter(parent__isnull=True)
        elif self.value():
            return queryset.filter(parent__slug=self.value())
        else:
            return queryset


class GenreAdmin(ModerationAdmin):
    verbose_name = "Genre"
    search_fields = ["name"]
    list_filter = [GenreParentFilter]


admin.site.register(Genre, GenreAdmin)


class AlbumArtistInline(admin.TabularInline):
    model = Artist.albums.through


class AlbumGenreInline(admin.TabularInline):
    model = Album.genres.through
    extra = 1
    verbose_name = "Album's genre"
    verbose_name_plural = "Albums's genres"


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    inlines = [
        AlbumArtistInline,
    ]
    extra = 1
    verbose_name = "Artist"
    search_fields = ["name"]
    exclude = ("albums",)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    inlines = [AlbumGenreInline, AlbumArtistInline]
    extra = 1
    search_fields = ["title"]


FLAG_MODEL = get_flag_model()


class FlagModelAdmin(admin.ModelAdmin):
    list_display = ("time_created", "content_type", "link_to_object", "status")
    readonly_fields = ("time_created", "content_type", "link_to_object", "status")
    search_fields = ("object_id", "content_type", "user")
    list_filter = ("time_created", "status", "content_type")
    ordering = ("-time_created",)
    date_hierarchy = "time_created"

    def link_to_object(self, instance):
        try:
            link = format_html(
                "<a href='{}'>{}</a>",
                reverse(
                    "albums:album_genres", args=[instance.linked_object.album.mbid]
                ),
                instance.linked_object,
            )
        except:
            link = ""
        return link


admin.site.unregister(FLAG_MODEL)
admin.site.register(FLAG_MODEL, FlagModelAdmin)
