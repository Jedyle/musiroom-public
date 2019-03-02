
from django.conf.urls import url
from rest_framework_nested import routers

from star_ratings.api.views import UserRatingView, CreateUserRatingView, followees_ratings, user_ratings
from . import views

router = routers.DefaultRouter()
router.register(r'ratings', views.RatingViewset)

urlpatterns = router.urls + [
    url(r'ratings/(?P<rating_id>[0-9]+)/self', UserRatingView.as_view()),
    url(r'ratings/followees', followees_ratings),
    url(r'ratings/self', user_ratings),
    url(r'ratings/(?P<rating_id>[0-9]+)/user_ratings', CreateUserRatingView.as_view())
]
