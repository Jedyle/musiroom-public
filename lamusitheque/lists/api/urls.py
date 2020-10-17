from django.conf.urls import url
from django.urls import include
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register(r"lists", views.ListViewset)

listitem_router = routers.NestedSimpleRouter(router, r"lists", lookup="lists")
listitem_router.register(r"items", views.ListItemViewset, base_name="listitems")

urlpatterns = [url(r"", include(router.urls)), url(r"", include(listitem_router.urls))]
