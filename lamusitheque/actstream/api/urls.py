from django.conf.urls import url
from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('activity/self', views.UserStreamView, 'Action')
router.register('activity/all', views.AllStreamView, 'Action')


urlpatterns = [
] + router.urls
