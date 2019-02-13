from django.conf.urls import url

from . import views  # import views so we can use them in urls.

app_name = 'ajax_follower'

urlpatterns = [
    url(r'^ajax_follow/$', views.ajax_follow, name='ajax_follow'),
    url(r'^ajax_contacts/(?P<username>[\w_-]{3,})$', views.ajax_contacts, name='ajax_contacts'),
]
