from django.urls import include, re_path, path
from rest_framework_nested import routers
from ajax_follower.api.views import FollowersViewset, FolloweesViewset
from albums.api.views import UserInterestsViewset
from discussions.api.views import UserDiscussionViewset
from lists.api.views import UserListViewset
from reviews.api.views import UserReviewViewset
from star_ratings.api.views import UserUserRatingViewset
from user_profile.api.views import (
    RegisterUserView,
    ActivateProfileView,
    ResendConfirmationLinkView,
    DestroyProfileView,
    ProfileViewset,
    NotificationViewset,
    BadgesViewset,
    UpdateAvatarView,
)

router = routers.DefaultRouter()
router.register(r"users", ProfileViewset)
router.register(r"notifications", NotificationViewset, basename="Notification")

user_nested_router = routers.NestedSimpleRouter(router, r"users", lookup="users")
user_nested_router.register(r"lists", UserListViewset, basename="lists")
user_nested_router.register(
    r"discussions", UserDiscussionViewset, basename="discussions"
)
user_nested_router.register(r"reviews", UserReviewViewset, basename="reviews")
user_nested_router.register(r"ratings", UserUserRatingViewset, basename="ratings")
user_nested_router.register(r"interests", UserInterestsViewset, basename="interests")
user_nested_router.register(r"badges", BadgesViewset, basename="badges")
user_nested_router.register(r"followers", FollowersViewset, basename="followers")
user_nested_router.register(r"followees", FolloweesViewset, basename="followees")

registration_patterns = [
    re_path(r"registration/$", RegisterUserView.as_view()),
    re_path(
        r"registration/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]+-[0-9A-Za-z]+)/$",
        ActivateProfileView.as_view(),
    ),
    re_path(
        r"registration/(?P<username>[\w_-]{3,})/resend_email/$",
        ResendConfirmationLinkView.as_view(),
    ),
    re_path(r"auth/user/delete", DestroyProfileView.as_view()),
    re_path(r"auth/user/avatar", UpdateAvatarView.as_view()),
    re_path(r"auth/", include("dj_rest_auth.urls")),
]

urlpatterns = registration_patterns + router.urls + user_nested_router.urls
