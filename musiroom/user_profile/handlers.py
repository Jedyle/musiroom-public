from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify
from pinax.badges.signals import badge_awarded
from rest_framework.authtoken.models import Token

from actstream import action
from lists.models import ListObj
from user_profile.models import Profile


BADGE_LABEL = "badge"


@receiver(badge_awarded)
def notify_badge_awarded(badge_award, **kwargs):
    print(badge_award)
    notify.send(
        badge_award.user,
        recipient=badge_award.user,
        verb="You have received the badge ",
        target=badge_award,
    )
    action.send(
        badge_award.user,
        verb="received the badge",
        action_object=badge_award,
        label=BADGE_LABEL,
    )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance=None, created=False, **kwargs):
    if created:
        # create auth token
        Token.objects.create(user=instance)
        # bind an user_profile and a 'top albums' list to the user_profile
        profile = Profile(user=instance)
        top_albums = ListObj(
            user=instance, title=instance.username + " Top Albums", ordered=True
        )
        top_albums.save()
        profile.top_albums = top_albums
        profile.save()
