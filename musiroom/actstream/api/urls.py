from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register("activity/self", views.UserStreamView, "actions_user")
router.register("activity/all", views.AllStreamView, "actions_all")
router.register("activity/rating", views.RatingStreamView, "actions_rating")
router.register("activity/review", views.ReviewStreamView, "actions_review")
router.register("activity/comment", views.CommentStreamView, "actions_comment")

urlpatterns = router.urls
