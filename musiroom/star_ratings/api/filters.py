import rest_framework_filters as filters
from rest_framework.filters import OrderingFilter
from star_ratings.models import UserRating
from django.db.models import F


class UserRatingFilter(filters.FilterSet):
    class Meta:
        model = UserRating
        fields = {
            "id": ["exact", "in"],
            "rating": ["exact"],
            "rating_id": ["exact", "in"],
            "is_interested": ["exact"],
            "is_in_collection": ["exact"],
            "score": ["exact", "isnull"],
            "modified": ["exact"],
        }


class UserRatingOrderingFilterBackend(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view) or []

        def transform_ordering(el):
            if el == "score":
                return F("score").asc(nulls_last=True)
            elif el == "-score":
                return F("score").desc(nulls_last=True)
            else:
                return el

        cleaned_ordering = [transform_ordering(el) for el in ordering]
        if cleaned_ordering:
            return queryset.order_by(*cleaned_ordering)

        return queryset
