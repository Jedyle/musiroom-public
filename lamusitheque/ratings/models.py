from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from vote.models import VoteModel

from comments.models import Comment
from star_ratings.models import UserRating


# Create your models here.

# TODO : rename app from ratings to review

class Review(VoteModel, models.Model):
    title = models.CharField("Title", max_length=200, blank=True)
    content = models.TextField("Content")
    date_publication = models.DateTimeField("Published", auto_now_add=True)
    date_last_change = models.DateTimeField("Last edit", auto_now=True)
    rating = models.OneToOneField(UserRating, on_delete=models.CASCADE, related_name='review')

    def __str__(self):
        if self.title:
            return self.title
        return str(self.rating.user) + '\'s review about ' + str(self.rating.rating.albums.get())

    def get_absolute_url(self):
        return reverse('review-detail', args=[self.id])

    @property
    def api_lookup_value(self):
        return self.id

    @property
    def user(self):
        """
        Every model that can be commented should have a 'user' attribute or property.
        :return:
        """
        return self.rating.user

    class Meta:
        verbose_name = 'review'
        verbose_name_plural = 'reviews'


def comment_review_notification(user, review):
    res = "<a href='{}'>{}</a>".format(reverse('user_profile', args=[user.username]),
                                       user.username) + " a commenté " + "<a href='{}'>votre critique</a>".format(
        reverse('albums:review', args=[review.rating.rating.albums.get().mbid,
                                       review.id])) + " sur l\'album " + "<a href='{}'>{}</a>".format(
        reverse('albums:album', args=[review.rating.rating.albums.get().mbid]), review.rating.rating.albums.get().title)
    return res


def comment_review_notification_for_users(user, review):
    res = "<a href='{}'>{}</a>".format(reverse('user_profile', args=[user.username]),
                                       user.username) + " a commenté la " + "<a href='{}'>critique</a>".format(
        review.get_absolute_url(), review.title) + " de " + "<a href='{}'>{}</a>".format(
        reverse('user_profile', args=[review.rating.user.username]),
        review.rating.user.username) + " sur l\'album " + "<a href='{}'>{}</a>".format(
        reverse('albums:album', args=[review.rating.rating.albums.get().mbid]), review.rating.rating.albums.get().title)
    return res


def comment_review_reply_notification(comment, parent):
    review = comment.content_object
    res = "<a href='{}'>{}</a>".format(reverse('user_profile', args=[comment.user_name]),
                                       comment.user_name) + " a répondu à " + "<a href='{}'>votre commentaire</a>".format(
        parent.get_absolute_url()) + " sur la " + "<a href='{}'>critique</a>".format(
        review.get_absolute_url()) + " de " + "<a href='{}'>{}</a>".format(
        reverse('user_profile', args=[review.rating.user.username]),
        review.rating.user.username) + " sur l\'album " + "<a href='{}'>{}</a>".format(
        reverse('albums:album', args=[review.rating.rating.albums.get().mbid]), review.rating.rating.albums.get().title)
    return res


