from django.conf.urls import url
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()

router.register(r'exports', views.ExportRetrieveViewset)

urlpatterns = [
                  url(r'^exports/sc_data/$', views.parse_sc_user),
                  url(r'^exports/$', views.ExportView.as_view()),
              ] + router.urls