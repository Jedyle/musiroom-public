from rest_framework_nested import routers

from conversations.api.views import ConversationViewset, MessageViewset

router = routers.DefaultRouter()
router.register(r"conversations", ConversationViewset)

message_router = routers.NestedSimpleRouter(
    router, r"conversations", lookup="conversations"
)
message_router.register(r"messages", MessageViewset, basename="message")

urlpatterns = [] + router.urls + message_router.urls
