from django.urls import include, re_path
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register(r"lists", views.ListViewset)

listitem_router = routers.NestedSimpleRouter(router, r"lists", lookup="lists")
listitem_router.register(r"items", views.ListItemViewset, basename="listitems")

urlpatterns = [
    re_path(r"lists_with_album", views.user_lists_with_album),
    re_path(r"", include(router.urls)),
    re_path(r"", include(listitem_router.urls)),
]
