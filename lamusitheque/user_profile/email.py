from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user_profile.tokens import profile_activation_token


def send_activation_email(request, user):
    """
    Send an activation email to the newly registrated user
    :param request: the request object
    :param user: a (not active) user
    :return: nothing, sends an activation email to the user
    """
    current_site = get_current_site(request)
    mail_subject = 'Activez votre compte.'
    message = render_to_string('user_profile/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': profile_activation_token.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()
