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
