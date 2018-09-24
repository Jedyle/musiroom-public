from __future__ import absolute_import, unicode_literals
from celery import task
from .badges import regular_badge_update

@task()
def update_badges():
    regular_badge_update()
