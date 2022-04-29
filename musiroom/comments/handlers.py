from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify

from actstream import action
from comments.models import Comment


COMMENT_LABEL = "comment"


@receiver(post_save, sender=Comment)
def comment_activity(sender, instance, created, **kwargs):
    print("coucou")
    if created:
        action.send(
            instance.user,
            verb="commented",
            action_object=instance,
            target=instance.content_object,
            label=COMMENT_LABEL,
        )


@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created:
        content_obj = instance.content_object
        user = instance.user
        if instance.user != user:
            notify.send(
                sender=instance.user,
                recipient=user,
                verb="has commented",
                target=content_obj,
            )
        if instance.parent is not None:
            parent = instance.parent
            parent_user = parent.user
            if parent_user != instance.user and parent_user != user:
                notify.send(
                    sender=instance.user,
                    recipient=parent_user,
                    verb="replied to your comment on",
                    target=content_obj,
                )
