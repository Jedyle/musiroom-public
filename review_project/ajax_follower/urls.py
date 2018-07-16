from django.conf.urls import url
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView


from . import views # import views so we can use them in urls.

app_name = 'ajax_follower'

urlpatterns = [
    url(r'^ajax_follow/$', views.ajax_follow, name='ajax_follow'),
    url(r'^ajax_contacts/(?P<username>[\w_-]{3,})$', views.ajax_contacts, name='ajax_contacts'),
]

