from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from profile.api.views import RegisterUserView, ActivateAccountView, ResendConfirmationLinkView, DestroyAccountView, \
    ProfileViewset

router = DefaultRouter()
router.register(r'users', ProfileViewset)

registration_patterns = [
    url(r'registration/$', RegisterUserView.as_view()),
    url(r'registration/activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        ActivateAccountView.as_view()),
    url(r'registration/(?P<username>[\w_-]{3,})/resend-email/$', ResendConfirmationLinkView.as_view()),
    url(r'auth/user/delete', DestroyAccountView.as_view())
]

urlpatterns = registration_patterns + router.urls
