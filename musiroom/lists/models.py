from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from vote.models import VoteModel

from albums.models import Album


# Create your models here.

class ListObj(VoteModel, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField('Title', max_length=400)
    description = models.TextField('Description', blank=True)
    ordered = models.BooleanField('Ordered list (top)', default=False)
    albums = models.ManyToManyField(Album, related_name='lists', through='ListItem')
    modified = models.DateTimeField("Last modification", auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('listobj-detail', args=[self.id])

    class Meta:
        verbose_name = 'list'
        verbose_name_plural = 'lists'
        ordering = ['-vote_score']


class ListItem(models.Model):
    item_list = models.ForeignKey(ListObj, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    comment = models.TextField(max_length=500, blank=True)
    order = models.IntegerField(default=-1)

    def __str__(self):
        return str(self.album)

    def get_absolute_url(self):
        return reverse('listitems-detail', args=[self.item_list.pk, self.pk])

    class Meta:
        ordering = ['order']
        unique_together = (('item_list', 'album'),)


