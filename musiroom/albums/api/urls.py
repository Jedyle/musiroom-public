from django.conf.urls import url
from django.urls import include
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register(r"genres", views.GenreViewset, base_name="genre")
router.register(r"all_genres", views.GenreListViewset, base_name="genre")
router.register(r"albums", views.AlbumViewset)
router.register(r"artists", views.ArtistViewset)


# Nested router to handle albums/<mbid>/genres/<mbid>
albumgenres_router = routers.NestedSimpleRouter(router, r"albums", lookup="albums")
albumgenres_router.register(r"genres", views.AlbumGenreViewset, base_name="genres")

urlpatterns = [
    url(r"", include(router.urls)),
    url(r"", include(albumgenres_router.urls)),
    url(
        r"tops/(?P<slug>([a-zA-Z-_]+))/(?P<year>([0-9]{4}s?|all))/$",
        views.TopAlbumsView.as_view(),
    ),
    url("interests/self", views.user_interests),
]
