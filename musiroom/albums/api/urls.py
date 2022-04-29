from django.urls import include, re_path
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register(r"genres", views.GenreViewset, basename="genre")
router.register(r"all_genres", views.GenreListViewset, basename="genre")
router.register(r"albums", views.AlbumViewset)
router.register(r"artists", views.ArtistViewset)


# Nested router to handle albums/<mbid>/genres/<mbid>
albumgenres_router = routers.NestedSimpleRouter(router, r"albums", lookup="albums")
albumgenres_router.register(r"genres", views.AlbumGenreViewset, basename="genres")

urlpatterns = [
    re_path(r"", include(router.urls)),
    re_path(r"", include(albumgenres_router.urls)),
    re_path(
        r"tops/(?P<slug>([a-zA-Z-_]+))/(?P<year>([0-9]{4}s?|all))/$",
        views.TopAlbumsView.as_view(),
    ),
    re_path("interests/self", views.user_interests),
]
