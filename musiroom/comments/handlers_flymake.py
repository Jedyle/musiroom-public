from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify

from actstream import action
from comments.models import Comment


@receiv