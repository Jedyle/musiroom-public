from django.urls import re_path
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()

router.register(r"exports", views.ExportRetrieveViewset)

urlpatterns = [
    re_path(r"^exports/sc_data/$", views.parse_sc_user),
    re_path(r"^exports/$", views.ExportView.as_view()),
] + router.urls
