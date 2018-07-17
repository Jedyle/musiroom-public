from django.db import models
from star_ratings.models import UserRating
from vote.models import VoteModel
from django_comments.moderation import moderator
from .moderation import UserLoggedInModerator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from fluent_comments.models import FluentComment
from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify
from django.urls import reverse


# Create your models here.

class Review(VoteModel, models.Model):
    title = models.CharField("Titre", max_length = 200, blank = True)
    content = models.TextField("Critique")
    date_publication = models.DateTimeField("Date publication", auto_now_add = True)
    date_last_change = models.DateTimeField("Dernière modification", auto_now = True)
    rating = models.OneToOneField(UserRating, on_delete= models.CASCADE, related_name='review')
    
    def __str__(self):
        return "Critique de : " + str(self.rating)

moderator.register(Review, UserLoggedInModerator)

def comment_review_notification(user, review):
    res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + " a commenté " + "<a href='{}'>votre critique</a>".format(reverse('albums:review', args=[review.rating.rating.albums.get().mbid, review.id])) + " sur l\'album " + "<a href='{}'>{}</a>".format(reverse('albums:album', args=[review.rating.rating.albums.get().mbid]), review.rating.rating.albums.get().title)
    return res

def comment_review_notification_for_users(user, review):
    res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + " a commenté la critique " + "<a href='{}'>{}</a>".format(reverse('albums:review', args=[review.rating.rating.albums.get().mbid, review.id]), review.title) + " de " + "<a href='{}'>{}</a>".format(reverse('profile', args=[review.rating.user.username]),review.rating.user.username) + " sur l\'album " + "<a href='{}'>{}</a>".format(reverse('albums:album', args=[review.rating.rating.albums.get().mbid]), review.rating.rating.albums.get().title)
    return res

@receiver(post_save, sender=FluentComment)
def notify_comment_review(sender, instance, created, **kwargs):
    if instance.content_type == ContentType.objects.get_for_model(Review):
        print('signal')
        pk = instance.object_pk
        review = Review.objects.get(pk = pk)
        user = review.rating.user
        if instance.user != user:
            notify.send(sender = instance.user, recipient = user, verb = "a commenté votre critique", target = review, to_str = comment_review_notification(instance.user, review))
        users_in_thread = User.objects.filter(comment_comments__content_type = ContentType.objects.get_for_model(Review), comment_comments__object_pk = pk).exclude(pk = instance.user.pk).exclude(pk = user.pk).distinct()
        notify.send(sender = instance.user, recipient = users_in_thread, verb = "a commenté la critique", target = review, to_str = comment_review_notification_for_users(instance.user, review))
        
