from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def is_active(account):
    print(account.last_activity, timezone.now())
    return ( timezone.now() - account.last_activity < timezone.timedelta(minutes = 5))


