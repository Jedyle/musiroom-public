import rest_framework_filters as filters

from star_ratings.models import UserRating


class UserRatingFilter(filters.FilterSet):
    class Meta:
        model = UserRating
        fields = {
            "id": ["exact", "in"],
            "rating": ["exact"],
            "rating_id": ["exact", "in"],
        }
