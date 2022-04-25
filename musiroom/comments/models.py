from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from django.urls import reverse
from vote.models import VoteModel

from comments.settings import get_max_depth


class Comment(VoteModel, models.Model):
    """
    A user comment about some object.
    """

    content_type = models.ForeignKey(ContentType,
                                     verbose_name='content type',
                                     related_name="content_type_set_for_%(class)s",
                                     on_delete=models.CASCADE)
    object_pk = models.TextField('object ID')

    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    user = models.ForeignKey(User, verbose_name='user',
                             blank=True, null=True, related_name="%(class)s_comments",
                             on_delete=models.SET_NULL)

    comment = models.TextField('comment', max_length=1024)

    # Metadata about the comment
    submit_date = models.DateTimeField('date/time submitted', db_index=True, auto_now_add=True)
    edit_date = models.DateTimeField('last edit', db_index=True, auto_now=True)
    is_removed = models.BooleanField('is removed', default=False,
                                     help_text='Check this box if the comment is inappropriate. '
                                               'A "This comment has been removed" message will '
                                               'be displayed instead.')

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="children_set")

    @property
    def depth(self):
        parent = self.parent
        depth = 0
        while parent is not None:
            depth += 1
            parent = parent.parent
        return depth

    @property
    def children(self, ordering='-submit_date'):
        return self.children_set.all().order_by(ordering)

    def save(self, *args, **kwargs):
        # Raise on circular reference
        parent = self.parent
        depth = 0
        while parent is not None:
            if parent == self:
                raise RuntimeError("Circular references are forbidden")
            parent = parent.parent
            depth += 1
        MAX_DEPTH = get_max_depth()
        if depth > MAX_DEPTH:
            raise RuntimeError("Nested comments should not exceed {}.".format(MAX_DEPTH))

        super(Comment, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('comment-detail', args=[self.pk])
