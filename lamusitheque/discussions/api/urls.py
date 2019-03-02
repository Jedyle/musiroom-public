from django.conf.urls import url
from django.urls import include
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register(r'discussions', views.DiscussionViewset)

urlpatterns = [
    url(r'', include(router.urls))
]