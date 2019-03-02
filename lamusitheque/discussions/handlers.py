from django.db.models.signals import post_save
from django.dispatch import receiver

from actstream import action
from discussions.models import Discussion

@receiver(post_save, sender=Discussion)
def create_discussion_handler(sender, instance, created, **kwargs):
    if created:
        if instance.content_object:  # not null
            action.send(instance.user, verb='created the discussion', action_object=instance,
                        target=instance.content_object)
        else:
            action.send(instance.user, verb='created the general discussion', action_object=instance)
