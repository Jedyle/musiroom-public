from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from actstream import action
from lists.models import ListItem


@receiver(post_save, sender=ListItem)
def save_list_handler(sender, instance, created, **kwargs):
    if created:
        list_obj = instance.item_list
        nb_items = list_obj.albums.count()
        instance.order = nb_items
        instance.save()
        list_obj.save()
        action.send(list_obj.user, verb="added", action_object=instance.album, target=instance.item_list)


@receiver(post_delete, sender=ListItem)
def delete_listitem_handler(sender, instance, **kwargs):
    """
    When listitem is delete, re-order the list
    """
    list_obj = instance.item_list
    objects = ListItem.objects.filter(item_list=list_obj)
    order = 1
    for item in objects:
        item.order = order
        item.save()
        order += 1
