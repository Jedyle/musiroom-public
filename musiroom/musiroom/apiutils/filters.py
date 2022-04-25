import rest_framework_filters as filters
from django.contrib.contenttypes.models import ContentType


class ContentTypeFilter(filters.FilterSet):
    class Meta:
        model = ContentType
        fields = {"model": ["exact"]}
