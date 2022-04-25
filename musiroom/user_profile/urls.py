from django.urls import path, re_path
from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.views.defaults import page_not_found

urlpatterns = [
    # disabling API password reset views
    re_path(
        r"^api/auth/password/reset/",
        page_not_found,
        {"exception": Exception()},
    ),
    # routes
    path(
        "auth/password/reset/",
        auth_views.PasswordResetView.as_view(
            extra_email_context={"domain": settings.BACKEND_URL.lstrip("https://")}
        ),
        name="reset_password",
    ),
    path(
        "auth/password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "auth/password/reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "auth/password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            extra_context={"site": Site.objects.get_current()}
        ),
        name="password_reset_complete",
    ),
]
