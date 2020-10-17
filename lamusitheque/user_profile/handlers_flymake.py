from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify
from pinax.badges.signals import badge_awa