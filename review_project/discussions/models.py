from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django_comments_xtd.models import XtdComment
from django_comments_xtd.signals import confirmation_received
from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify
from django.urls import reverse
from vote.models import VoteModel
from django.db.models.signals import post_save
from actstream import action

# Create your models here.

class Discussion(VoteModel, models.Model):
    created = models.DateTimeField("Date de publication", auto_now_add = True)
    modified = models.DateTimeField("Dernière modification", auto_now = True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussions')
    title = models.CharField('Titre', max_length = 200, blank = True)
    content = models.TextField('Contenu')
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(default=0)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('discussions:display_discussion', args=[self.pk])

    class Meta:
        verbose_name = "discussion"
        verbose_name_plural = "discussions"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=['created'])
            ]

@receiver(post_save, sender=Discussion)
def create_discussion_handler(sender, instance, created, **kwargs):
    if created:
        if instance.content_object: #not null
            action.send(instance.author, verb='a posté la discussion', action_object=instance, target=instance.content_object)
        else:
            action.send(instance.author, verb='a posté la discussion générale', action_object=instance) 

def comment_discussion_notification(user, discussion):
    if discussion.content_object:
        res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + " a commenté votre discussion " + "<a href='{}'>{}</a>".format(discussion.get_absolute_url(), discussion.title) + " sur " + "<a href='{}'>{}</a>".format(discussion.content_object.get_absolute_url(), str(discussion.content_object))
    else :
        res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + " a commenté votre discussion " + "<a href='{}'>{}</a>".format(discussion.get_absolute_url(), discussion.title)
    return res

def comment_discussion_notification_for_users(user, discussion):
    if discussion.content_object:
        res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + " a commenté la discussion " + "<a href='{}'>{}</a>".format(discussion.get_absolute_url(), discussion.title) + " sur " + "<a href='{}'>{}</a>".format(discussion.content_object.get_absolute_url(), str(discussion.content_object))
    else:
        res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + " a commenté la discussion " + "<a href='{}'>{}</a>".format(discussion.get_absolute_url(), discussion.title)
    return res

def comment_discussion_reply_notification(comment, parent):
    discussion = comment.content_object
    res = "<a href='{}'>{}</a>".format(reverse('profile', args=[comment.user_name]),comment.user_name) + " a répondu à " + "<a href='{}'>votre commentaire</a>".format(parent.get_absolute_url()) + " sur la discussion " + "<a href='{}'>{}</a>".format(discussion.get_absolute_url(), discussion.title) 
    return res

@receiver(confirmation_received)
def notify_comment_discussion(comment, request, **kwargs):
    if comment.content_type == ContentType.objects.get_for_model(Discussion):
        pk = comment.object_pk
        discussion = Discussion.objects.get(pk = pk)
        user = discussion.author
        if comment.user != user:
            notify.send(sender = comment.user, recipient = user, verb = "a commenté votre discussion", target = discussion, to_str = comment_discussion_notification(comment.user, discussion))
        if comment.parent_id != 0:
            parent = XtdComment.objects.get(pk = comment.parent_id)
            parent_user = parent.user
            if parent_user != comment.user and parent_user != user:
                notify.send(sender = comment.user, recipient = parent_user, verb ="a répondu à votre commentaire", target = comment.xtd_comment, to_str = comment_discussion_reply_notification(comment, parent))
        else :
            parent_user = None
            users_in_thread = User.objects.filter(comment_comments__content_type = ContentType.objects.get_for_model(Discussion), comment_comments__object_pk = pk).exclude(pk = comment.user.pk).exclude(pk = user.pk).distinct()
            notify.send(sender = comment.user, recipient = users_in_thread, verb = "a commenté la discussion", target = discussion, to_str = comment_discussion_notification_for_users(comment.user, discussion))
        

