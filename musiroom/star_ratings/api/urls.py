from django.urls import re_path
from rest_framework_nested import routers

from star_ratings.api.views import (
    UserRatingView,
    CreateUserRatingView,
    followees_ratings,
    user_ratings,
)
from . import views

router = routers.DefaultRouter()
router.register(r"ratings", views.RatingViewset)

urlpatterns = router.urls + [
    re_path(r"ratings/(?P<rating_id>[0-9]+)/self", UserRatingView.as_view()),
    re_path(r"ratings/followees", followees_ratings),
    re_path(r"ratings/self", user_ratings),
    re_path(
        r"ratings/(?P<rating_id>[0-9]+)/user_ratings", CreateUserRatingView.as_view()
    ),
]
