from django.urls import include, path, re_path
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register(r"discussions", views.DiscussionViewset)

urlpatterns = [
    re_path(r"", include(router.urls)),
    path(
        "discussions/object/<slug:model>/<slug:object_id>", views.get_discussion_object
    ),
]
