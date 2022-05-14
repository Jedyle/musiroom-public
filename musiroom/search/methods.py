from django.contrib.postgres.search import SearchQuery, SearchVector
from albums.models import Album, Artist
from django.contrib.auth.models import User

AUTOCOMPLETE_SEARCH_METHODS = {
    "album": lambda query: Album.objects.annotate(
        search=SearchVector("title", "artists__name")
    ).filter(search=SearchQuery(query)),
    "artist": lambda query: Artist.objects.filter(name__icontains=query),
    "user": lambda query: User.objects.filter(username__icontains=query),
}
