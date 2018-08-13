from django.conf.urls import url

from . import views # import views so we can use them in urls.
from ratings import views as rating_views

app_name = 'albums'

urlpatterns = [
    url(r'^$', views.browse_albums, name='browse_albums'),
    url(r'^album/(?P<mbid>[0-9a-z-]{36})/$', views.album, name='album'),
    url(r'^album/update_cover/$', views.update_cover, name='update_cover'),
    url(r'^album/(?P<mbid>[0-9a-z-]{36})/genres/$', views.album_genres, name='album_genres'),
    url(r'^album/(?P<mbid>[0-9a-z-]{36})/critiques/(?P<review_id>[0-9]+)/$', rating_views.review, name='review'),
    url(r'^album/(?P<mbid>[0-9a-z-]{36})/listes/$', views.album_lists, name='album_lists'),
    url(r'^album/ajax_vote/$', views.ajax_vote, name='ajax_vote'),
    url(r'^album/report_genre/$', views.report_genre, name='report_genre'),
    url(r'^artiste/(?P<mbid>[0-9a-z-]{36})/$', views.artist, name='artist'),
    url(r'^ajax_artiste/(?P<mbid>[0-9a-z-]{36})/$', views.ajax_artist, name='ajax_artist'),
    url(r'^ajax_artiste_notes_page/$', views.ajax_artist_page_ratings, name='ajax_artist_page_ratings'),
    url(r'^rechercher$', views.search, name='search'),
    url(r'^recherche_avancee/$', views.ajax_search_in_db, name='ajax_search_in_db'),
    url(r'^genres/$', views.genres, name='genres'),
    url(r'genres/ajouter/$', views.submit_genre, name='submit_genre'),
    url('^genre/(?P<slug>[0-9a-zA-Z_-]+)/$', views.genre, name='genre'),
    url(r'^top/$', views.top_album_get, name='top_album_get'),
    url(r'^top/(?P<slug>([a-zA-Z-_]+))/(?P<year>([0-9]{4}s?|tout))/$', views.top_album, name='top_album'),
    url(r'album/donnees/$', views.album_data, name='album_data'),
        ]
