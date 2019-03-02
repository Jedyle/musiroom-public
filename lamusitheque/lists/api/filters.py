import rest_framework_filters as filters
from django.contrib.auth.models import User

from lists.models import ListObj
from user_profile.api.filters import UserFilter


class ListFilter(filters.FilterSet):

    user = filters.RelatedFilter(UserFilter, field_name="user", queryset=User.objects.all())

    class Meta:
        model = ListObj
        fields = {"title": "__all__",
                  "description": ["icontains"]}
