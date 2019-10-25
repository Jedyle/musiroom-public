import rest_framework_filters as filters

from reviews.models import Review


class ReviewFilter(filters.FilterSet):
    class Meta:
        model = Review
        fields = {"rating_id": ["exact", "in"]}
