import rest_framework_filters as filters

from albums.models import Album, Artist


class AlbumFilter(filters.FilterSet):
    class Meta:
        model = Album
        fields = {"title": ['iexact', 'in', 'startswith', 'icontains']}


class ArtistFilter(filters.FilterSet):
    class Meta:
        model = Artist
        fields = {"name": ["iexact", "in", "startswith", "icontains"]}
