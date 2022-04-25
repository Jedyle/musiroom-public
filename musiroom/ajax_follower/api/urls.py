from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^followees/$', views.FollowView.as_view())
]
