from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user_profile.tokens import profile_activation_token


def send_activation_email(site_pk, username):
    """
    Send an activation email to the newly registrated user
    :param request: the request object
    :param user: a (not active) user
    :return: nothing, sends an activation email to the user
    """
    user = User.objects.get(username=username)
    site = Site.objects.get(pk=site_pk)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = profile_activation_token.make_token(user)
    message = render_to_string(
        "account/email/email_confirmation_message.txt",
        {
            "user": user,
            "current_site": site,
            "activate_url": f"{settings.FRONTEND_APP_NAME}/confirm?token={token}&uid={uid}",
        },
    )
    mail_subject = "Activate you account."
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.send()
