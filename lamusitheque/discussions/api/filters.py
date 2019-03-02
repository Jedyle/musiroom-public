import rest_framework_filters as filters
from django.contrib.contenttypes.models import ContentType

from discussions.models import Discussion
from lamusitheque.apiutils.filters import ContentTypeFilter


class DiscussionFilter(filters.FilterSet):
    content_type = filters.RelatedFilter(ContentTypeFilter, field_name="content_type",
                                         queryset=ContentType.objects.all())

    class Meta:
        model = Discussion
        fields = {"object_id": ["exact"], "content_type_id": ["isnull"]}
