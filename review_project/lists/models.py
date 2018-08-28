from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from albums.models import Album
from vote.models import VoteModel

# from fluent_comments.models import FluentComment
from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify
from django.urls import reverse

# Create your models here.

class ItemList(VoteModel, models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField('Titre', max_length = 400)
    description = models.TextField('Description', blank=True)
    ordered = models.BooleanField('Liste ordonnée (top)', default = False)
    albums = models.ManyToManyField(Album, related_name='lists', through = 'ListObject')

    def __str__(self):
        return self.user.username + " : " + self.title

class ListObject(models.Model):
    item_list = models.ForeignKey(ItemList, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    comment = models.TextField(max_length = 500, blank = True)
    order = models.IntegerField(default = -1)

    def __str__(self):
        return str(self.item_list) + " - " + str(self.album)

    class Meta:
        ordering = ['order']


@receiver(post_save, sender=ListObject)
def save_list_handler(sender, instance, created, **kwargs):
    if created:
        itemlist = instance.item_list
        nb_items = itemlist.albums.count()
        instance.order = nb_items
        instance.save()

@receiver(post_delete, sender=ListObject)
def delete_list_handler(sender, instance, **kwargs):
    itemlist = instance.item_list
    objects = ListObject.objects.filter(item_list = itemlist)
    order = 1
    for item in objects:
        item.order = order
        item.save()
        order += 1

def comment_list_notification(user, list):
    res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + " a commenté votre liste " + "<a href='{}'>{}</a>".format(reverse('lists:display_list', args=[list.id]), list.title)
    return res

def comment_list_notification_for_users(user, list):
    res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + " a commenté la liste " + "<a href='{}'>{}</a>".format(reverse('lists:display_list', args=[list.id]), list.title) + " de " + "<a href='{}'>{}</a>".format(reverse('profile', args=[list.user.username]),list.user.username)
    return res

# @receiver(post_save, sender=FluentComment)
# def notify_comment_list(sender, instance, created, **kwargs):
#     if instance.content_type == ContentType.objects.get_for_model(ItemList):
#         print('signal 2')
#         pk = instance.object_pk
#         list_ = ItemList.objects.get(pk = pk)
#         user = list_.user
#         if instance.user != user:
#             notify.send(sender = instance.user, recipient = user, verb = "a commenté votre liste", target = list_, to_str = comment_list_notification(instance.user, list_))
#         users_in_thread = User.objects.filter(comment_comments__content_type = ContentType.objects.get_for_model(ItemList), comment_comments__object_pk = pk).exclude(pk = instance.user.pk).exclude(pk = user.pk).distinct()
#         notify.send(sender = instance.user, recipient = users_in_thread, verb = "a commenté la liste", target = list_, to_str = comment_list_notification_for_users(instance.user, list_))
