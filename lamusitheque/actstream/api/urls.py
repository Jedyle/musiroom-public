from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register('activity/self', views.UserStreamView, 'Action')
router.register('activity/all', views.AllStreamView, 'Action')

urlpatterns = router.urls
