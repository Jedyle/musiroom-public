from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from vote.models import VoteModel


# Create your models here.


class Discussion(VoteModel, models.Model):
    created = models.DateTimeField("Date", auto_now_add=True)
    modified = models.DateTimeField("Last edit", auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussions')
    title = models.CharField('Title', max_length=200, blank=True)
    content = models.TextField('Content')
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(default=0)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('discussion-detail', args=[self.pk])

    class Meta:
        verbose_name = "discussion"
        verbose_name_plural = "discussions"
        ordering = ["-modified"]
        indexes = [
            models.Index(fields=['modified']),
            models.Index(fields=['created']),
        ]


