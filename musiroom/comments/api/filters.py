import rest_framework_filters as filters
from django.contrib.contenttypes.models import ContentType

from comments.models import Comment
from musiroom.apiutils.filters import ContentTypeFilter


class CommentFilter(filters.FilterSet):
    content_type = filters.RelatedFilter(
        ContentTypeFilter, field_name="content_type", queryset=ContentType.objects.all()
    )

    class Meta:
        model = Comment
        fields = {"object_pk": ["exact"]}
