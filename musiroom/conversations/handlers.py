from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from conversations.models import Membership


# @receiver(post_save, sender=Membership)
# def set_last_read(sender, instance, created, **kwargs):
#     # when a message is created, all other users in a conversation should be added to 'unread_by' m2m field
#     if instance.unread is True:
#         instance.last_read = timezone.now()
#         instance.save()
