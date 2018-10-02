from django.db import models
from star_ratings.models import UserRating
from vote.models import VoteModel
from django_comments.moderation import moderator
from .moderation import UserLoggedInModerator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django_comments_xtd.signals import confirmation_received
from django_comments_xtd.models import XtdComment
from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify
from django.urls import reverse
from actstream import action
from review_project.utils import make_clickable_link as _link


# Create your models here.

class Review(VoteModel, models.Model):
    title = models.CharField("Titre", max_length = 200, blank = True)
    content = models.TextField("Critique")
    date_publication = models.DateTimeField("Date publication", auto_now_add = True)
    date_last_change = models.DateTimeField("Dernière modification", auto_now = True)
    rating = models.OneToOneField(UserRating, on_delete= models.CASCADE, related_name='review')
    
    def __str__(self):
        if self.title :
            return self.title + ' par ' + str(self.rating.user) +  ' sur l\'album ' + str(self.rating.rating.albums.get())
        return "Critique de " + str(self.rating.user) + ' sur l\'album ' + str(self.rating.rating.albums.get())

    def get_absolute_url(self):
        return reverse('albums:review', args=[self.rating.rating.albums.get().mbid, self.id])

    class Meta:
        verbose_name = 'critique'
        verbose_name_plural = 'critiques'

moderator.register(Review, UserLoggedInModerator)

def comment_review_notification(user, review):
    res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + " a commenté " + "<a href='{}'>votre critique</a>".format(reverse('albums:review', args=[review.rating.rating.albums.get().mbid, review.id])) + " sur l\'album " + "<a href='{}'>{}</a>".format(reverse('albums:album', args=[review.rating.rating.albums.get().mbid]), review.rating.rating.albums.get().title)
    return res

def comment_review_notification_for_users(user, review):
    res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + " a commenté la " + "<a href='{}'>critique</a>".format(review.get_absolute_url(), review.title) + " de " + "<a href='{}'>{}</a>".format(reverse('profile', args=[review.rating.user.username]),review.rating.user.username) + " sur l\'album " + "<a href='{}'>{}</a>".format(reverse('albums:album', args=[review.rating.rating.albums.get().mbid]), review.rating.rating.albums.get().title)
    return res

def comment_review_reply_notification(comment, parent):
    review = comment.content_object
    res = "<a href='{}'>{}</a>".format(reverse('profile', args=[comment.user_name]),comment.user_name) + " a répondu à " + "<a href='{}'>votre commentaire</a>".format(parent.get_absolute_url()) + " sur la " + "<a href='{}'>critique</a>".format(review.get_absolute_url()) + " de " + "<a href='{}'>{}</a>".format(reverse('profile', args=[review.rating.user.username]),review.rating.user.username) + " sur l\'album " + "<a href='{}'>{}</a>".format(reverse('albums:album', args=[review.rating.rating.albums.get().mbid]), review.rating.rating.albums.get().title)
    return res

@receiver(confirmation_received)
def notify_comment_review(comment, request, **kwargs):
    if comment.content_type == ContentType.objects.get_for_model(Review):
        pk = comment.object_pk
        review = Review.objects.get(pk = pk)
        user = review.rating.user
        if comment.user != user:
            notify.send(sender = comment.user, recipient = user, verb = "a commenté votre critique", target = review, to_str = comment_review_notification(comment.user, review))
        if comment.parent_id != 0:
            parent = XtdComment.objects.get(pk = comment.parent_id)
            parent_user = parent.user
            if parent_user != comment.user and parent_user != user:
                notify.send(sender = comment.user, recipient = parent_user, verb ="a répondu à votre commentaire", target = comment.xtd_comment, to_str = comment_review_reply_notification(comment, parent))
        else :
            parent_user = None
            users_in_thread = User.objects.filter(comment_comments__content_type = ContentType.objects.get_for_model(Review), comment_comments__object_pk = pk).exclude(pk = comment.user.pk).exclude(pk = user.pk).distinct()
            notify.send(sender = comment.user, recipient = users_in_thread, verb = "a commenté la critique", target = review, to_str = comment_review_notification_for_users(comment.user, review))

@receiver(post_save, sender=Review)
def save_review_handler(sender, instance, created, **kwargs):
    if created:
        action.send(instance.rating.user, verb='a ecrit une critique : ', action_object=instance)

def rating_to_str(instance):
    return _link(instance.user) + ' a attribué la note de ' + str(instance.score) + ' à l\'album ' + _link(instance.rating.content_object)

@receiver(post_save, sender=UserRating)
def save_rating_handler(sender, instance, created, **kwargs):
    action.send(instance.user, verb='a attribue la note de ' + str(instance.score) + ' a ', action_object=instance, target=instance.rating.content_object, to_str= rating_to_str(instance))
        
