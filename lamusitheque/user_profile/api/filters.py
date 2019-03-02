import rest_framework_filters as filters
from django.contrib.auth.models import User

from user_profile.models import Profile


class UserFilter(filters.FilterSet):

    class Meta:
        model = User
        fields = {"username": ['iexact', 'in', 'startswith', 'icontains']}


class ProfileFilter(filters.FilterSet):

    user = filters.RelatedFilter(UserFilter, field_name='user', queryset=User.objects.all())

    class Meta:
        model = Profile
        fields = {"sex": ['exact']}
