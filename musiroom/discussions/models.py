from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from vote.models import VoteModel
from comments.models import Comment

# Create your models here.


class Discussion(VoteModel, models.Model):
    created = models.DateTimeField("Date", auto_now_add=True)
    modified = models.DateTimeField("Last edit", auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussions')
    title = models.CharField('Title', max_length=200)
    content = models.TextField('Content')
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(default=0)
    content_object = GenericForeignKey('content_type', 'object_id')

    comments = GenericRelation(Comment,
                               related_query_name='discussions',
                               object_id_field='object_pk')
    
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


