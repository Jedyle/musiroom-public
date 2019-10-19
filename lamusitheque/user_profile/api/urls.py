from django.conf.urls import url
from rest_framework_nested import routers

from ajax_follower.api.views import FollowersViewset, FolloweesViewset
from albums.api.views import UserInterestsViewset
from discussions.api.views import UserDiscussionViewset
from lists.api.views import UserListViewset
from reviews.api.views import UserReviewViewset
from star_ratings.api.views import UserUserRatingViewset
from user_profile.api.views import RegisterUserView, ActivateProfileView, ResendConfirmationLinkView, \
    DestroyProfileView, \
    ProfileViewset, NotificationViewset, BadgesViewset

router = routers.DefaultRouter()
router.register(r'users', ProfileViewset)

user_nested_router = routers.NestedSimpleRouter(router, r'users', lookup='users')
user_nested_router.register(r'lists', UserListViewset, base_name="lists")
user_nested_router.register(r'discussions', UserDiscussionViewset, base_name="discussions")
user_nested_router.register(r'reviews', UserReviewViewset, base_name="reviews")
user_nested_router.register(r'ratings', UserUserRatingViewset, base_name="ratings")
user_nested_router.register(r'interests', UserInterestsViewset, base_name="interests")
user_nested_router.register(r'notifications', NotificationViewset, base_name="notifications")
user_nested_router.register(r'badges', BadgesViewset, base_name='badges')
user_nested_router.register(r'followers', FollowersViewset, base_name='followers')
user_nested_router.register(r'followees', FolloweesViewset, base_name='followees')

registration_patterns = [
    url(r'registration/$', RegisterUserView.as_view()),
    url(r'registration/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        ActivateProfileView.as_view()),
    url(r'registration/(?P<username>[\w_-]{3,})/resend-email/$', ResendConfirmationLinkView.as_view()),
    url(r'auth/user/delete', DestroyProfileView.as_view())
]

urlpatterns = registration_patterns + router.urls + user_nested_router.urls
