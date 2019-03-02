from __future__ import absolute_import, unicode_literals

from celery import task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from .badges import regular_badge_update
from .models import Profile


@task()
def update_badges():
    regular_badge_update()


DAYS_OF_INACTIVITY = 30


@task()
def send_email_to_inactive_user():
    inactive_users = Profile.objects.filter(
        last_activity__lt=timezone.now() - timezone.timedelta(days=DAYS_OF_INACTIVITY))
    for user in inactive_users:
        c = {'user': user.user}
        html_content = render_to_string('user_profile/inactive_user_mail.html', c)
        text_content = render_to_string('user_profile/inactive_user_mail.txt', c)
        email = EmailMultiAlternatives('Vous nous manquez, {} !'.format(user.user.username), text_content)
        email.attach_alternative(html_content, "text/html")
        email.to = [user.user.email]
        email.send()
