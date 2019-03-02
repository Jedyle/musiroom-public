import rest_framework_filters as filters

from ratings.models import Review


class ReviewFilter(filters.FilterSet):
    class Meta:
        model = Review
        fields = {"rating_id": ["exact"]}
