from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def is_active(account):
    return timezone.now() - account.last_activity < timezone.timedelta(minutes=5)
