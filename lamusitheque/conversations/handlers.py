from django.db.models.signals import post_save
from django.dispatch import receiver

from conversations.models import Message


@receiver(post_save, sender=Message)
def trigger_notifications(sender, instance, created, **kwargs):
    # when a message is created, all other users in a conversation should be added to 'unread_by' m2m field
    if created:
        author = instance.user
        conversation = instance.conversation
        receivers = conversation.users.exclude(id__in=[author.id])
        conversation.unread_by.add(*receivers)
        conversation.save()