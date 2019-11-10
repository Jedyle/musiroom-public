import rest_framework_filters as filters

from reviews.models import Review
from star_ratings.api.filters import UserRating, UserRatingFilter

class ReviewFilter(filters.FilterSet):

    rating = filters.RelatedFilter(UserRatingFilter, field_name="rating", queryset=UserRating.objects.all())
    
    class Meta:
        model = Review
        fields = {"rating_id": ["exact", "in"], "title": ["exact", "icontains"]}
