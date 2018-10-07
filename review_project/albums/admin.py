from django.contrib import admin
from moderation.admin import ModerationAdmin
from .models import Genre, Album, Artist
from django.utils.html import format_html
from siteflags.utils import get_flag_model
from django.urls import reverse

# Register your models here.

class GenreParentFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "parent"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'parent'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        parents = set([genre.parent for genre in model_admin.model.objects.all()])
        return [('aucun', 'Aucun')] + [(genre.slug, genre.name)  for genre in parents if genre is not None]
    
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'aucun' :
            return queryset.filter(parent__isnull = True)
        elif self.value():
            return queryset.filter(parent__slug = self.value())
        else:
            return queryset

class GenreAdmin(ModerationAdmin):
    verbose_name = "Genre"
    search_fields = ['name']
    list_filter = [GenreParentFilter]

admin.site.register(Genre, GenreAdmin)

class ArtistAlbumInline(admin.TabularInline):
    model = Album.artists.through
    verbose_name = "Album"
    verbose_name_plural = "Albums"
    extra = 0

class AlbumGenreInline(admin.TabularInline):
    model = Album.genres.through
    extra = 1
    verbose_name = "Genre de l'album"
    verbose_name_plural = "Genres de l'album"

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    inlines = [ArtistAlbumInline,]
    verbose_name = "Artiste"
    search_fields = ['name']

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    inlines = [AlbumGenreInline, ArtistAlbumInline]
    extra = 1
    search_fields = ['title']


FLAG_MODEL = get_flag_model()
    

class FlagModelAdmin(admin.ModelAdmin):
    list_display = ('time_created', 'content_type', 'link_to_object', 'status')
    readonly_fields = ('time_created', 'content_type', 'link_to_object', 'status')
    search_fields = ('object_id', 'content_type', 'user')
    list_filter = ('time_created', 'status', 'content_type')
    ordering = ('-time_created',)
    date_hierarchy = 'time_created'

    def link_to_object(self, instance):
        try:
            link = format_html("<a href='{}'>{}</a>", reverse('albums:album_genres', args=[instance.linked_object.album.mbid]), instance.linked_object)
        except:
            link = ""
        return link
    
admin.site.unregister(FLAG_MODEL)
admin.site.register(FLAG_MODEL, FlagModelAdmin)
