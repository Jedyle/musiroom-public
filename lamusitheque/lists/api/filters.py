import rest_framework_filters as filters
from django.contrib.auth.models import User

from lists.models import ListObj
from user_profile.api.filters import UserFilter


class ListFilter(filters.FilterSet):

    user = filters.RelatedFilter(
        UserFilter, field_name="user", queryset=User.objects.all()
    )

    contains_album = filters.CharFilter(
        field_name="albums", method="list_contains_album"
    )
    not_contains_albums = filters.CharFilter(
        field_name="albums", method="list_not_contains_album"
    )

    class Meta:
        model = ListObj
        fields = {"title": "__all__", "description": ["icontains"]}

    def list_contains_album(self, qs, name, value):
        """
        Filters List based on whether they contain a specific album (value is a mbid)
        """
        return qs.filter(albums__mbid=value)

    def list_not_contains_album(self, qs, name, value):
        """
        Filters List based on whether they dont contain a specific album (value is a mbid)
        """
        return qs.exclude(albums__mbid=value)
