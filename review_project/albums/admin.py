from django.contrib import admin
from moderation.admin import ModerationAdmin
from .models import Genre, Album, Artist
from django.utils.html import format_html
from siteflags.utils import get_flag_model
from django.urls import reverse

# Register your models here.

class GenreAdmin(ModerationAdmin):
    verbose_name = "Genre"

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
