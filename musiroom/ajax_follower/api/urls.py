from django.urls import re_path
from . import views

urlpatterns = [re_path(r"^followees/$", views.FollowView.as_view())]
