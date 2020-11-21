import rest_framework_filters as filters
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from user_profile.api.filters import UserFilter

from discussions.models import Discussion
from lamusitheque.apiutils.filters import ContentTypeFilter


class DiscussionFilter(filters.FilterSet):
    content_type = filters.RelatedFilter(
        ContentTypeFilter, field_name="content_type", queryset=ContentType.objects.all()
    )

    user = filters.RelatedFilter(
        UserFilter, field_name="user", queryset=User.objects.all()
    )

    class Meta:
        model = Discussion
        fields = {
            "object_id": ["exact"],
            "content_type_id": ["isnull"],
            "title": ["exact", "icontains"],
        }
