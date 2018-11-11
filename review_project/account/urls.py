from django.conf.urls import url
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView


from . import views # import views so we can use them in urls.

#app_name = 'account'

urlpatterns = [
    url(r'^inscription/$', views.register, name='register'),
    url(r'^inscription/renvoyer/(?P<username>[\w_-]{3,})/$', views.resend_email, name='resend_email'),
    url(r'^inscription_complete/$', views.registration_complete, name='registration_complete'),
    url(r'^connexion/$', LoginView.as_view(template_name='account/login.html', redirect_authenticated_user=True), name='login'),
    url(r'^deconnexion/$', LogoutView.as_view(), name='logout'),
    url(r'^connecte/$', views.loggedin, name='loggedin'),
    url(r'^modifier/$', views.edit_profile, name="edit_profile"),
    url(r'^activation/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    url(r'^parametres/$', views.edit_settings, name='edit_settings'),
    url(r'^oublie/$', PasswordResetView.as_view(template_name='account/password_change_form.html'), name='reset_password'),
    url(r'^oublie/fin/$', PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    url(r'^oublie/confirmer/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'), name='password_reset_confirm'),
    url(r'^oublie/succes/$', PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name='password_reset_complete'),
    url(r'^supprimer/$', views.delete_account, name='delete_account'),
    url(r'^u/(?P<username>[\w_-]{3,})$', views.profile, name='profile'),
    url(r'^notifications/$', views.notifications, name='notifications'),
    url(r'^exports/$', views.user_exports, name='user_exports'),
]
