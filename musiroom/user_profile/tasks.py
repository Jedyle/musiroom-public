from celery import shared_task
from .badges import regular_badge_update
from .email import send_activation_email


@shared_task
def update_badges():
    regular_badge_update()


@shared_task
def send_user_activation_email(site_pk, username):
    send_activation_email(site_pk, username)
