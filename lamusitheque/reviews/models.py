from django.db import models
from django.urls import reverse
from vote.models import VoteModel

from star_ratings.models import UserRating


# Create your models here.

class Review(VoteModel, models.Model):
    title = models.CharField("Title", max_length=200)
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
    def user(self):
        """
        Every model that can be commented should have a 'user' attribute or property.
        :return:
        """
        return self.rating.user

    class Meta:
        verbose_name = 'review'
        verbose_name_plural = 'reviews'
