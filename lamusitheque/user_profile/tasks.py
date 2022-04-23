import celery
from .badges import regular_badge_update
from .email import send_activation_email


@celery.task
def update_badges():
    regular_badge_update()


@celery.task
def send_user_activation_email(username):
    send_activation_email(username)
