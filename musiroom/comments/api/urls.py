from rest_framework_nested import routers

from comments.api.views import CommentViewset, CommentChildrenViewset

router = routers.DefaultRouter()
router.register(r"comments", CommentViewset, basename="comment")

comments_nested_router = routers.NestedSimpleRouter(
    router, r"comments", lookup="comments"
)
comments_nested_router.register(
    r"children", CommentChildrenViewset, basename="comments"
)

urlpatterns = [] + router.urls + comments_nested_router.urls
