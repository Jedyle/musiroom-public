"""Models for the conversations app."""
import os

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from conversations.validators import FileSizeValidator


class Conversation(models.Model):
    """
    Model to contain different messages between one or more users.

    :users: Users participating in this conversations.
    :archived_by: List of participants, who archived this conversations.
    :notified: List of participants, who have received an email notification.
    :unread_by: List of participants, who haven't read this conversations.
    :read_by_all: Date all participants have marked this conversations as read.

    """

    title = models.CharField("Title", null=False, max_length=100)

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Users"),
        related_name="conversations",
        through="Membership",
    )

    # archived_by = models.ManyToManyField(
    #     settings.AUTH_USER_MODEL,
    #     verbose_name=_('Archived by'),
    #     related_name='archived_conversations',
    #     blank=True,
    # )

    # notified = models.ManyToManyField(
    #     settings.AUTH_USER_MODEL,
    #     verbose_name=_('Notified'),
    #     related_name='notified_conversations',
    #     blank=True,
    # )

    # unread_by = models.ManyToManyField(
    #     settings.AUTH_USER_MODEL,
    #     verbose_name=_("Unread by"),
    #     related_name="unread_conversations",
    #     blank=True,
    # )

    # read_by_all = models.DateTimeField(
    #     verbose_name=_("Read by all"),
    #     auto_now_add=True,
    # )

    class Meta:
        ordering = ("-pk",)
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")

    def __str__(self):
        return "{}".format(self.pk)

    def get_absolute_url(self):
        return reverse("conversation-detail", args=[self.pk])

    def mark_as_read(self, *users):
        memberships = self.membership_set.filter(user__in=users)
        for membership in memberships:
            membership.unread = False
            membership.last_read = timezone.now()
            membership.save()

    def mark_unread_by_all_except(self, except_user):
        for membership in self.membership_set.exclude(user=except_user):
            membership.unread = True
            membership.save()


class Membership(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
    )

    conversation = models.ForeignKey(
        "Conversation",
        verbose_name=_("Conversation"),
        on_delete=models.CASCADE,
    )

    # whether user is active or has been deleted
    is_active = models.BooleanField(
        verbose_name=_("Is active"),
        null=False,
        default=True
    )

    unread = models.BooleanField(
        verbose_name=_("Unread"),
        null=False,
        default=True
    )

    last_read = models.DateTimeField(auto_now_add=True, verbose_name=_("Last read"))


class Message(models.Model):
    """
    Model, which holds information about a post within one conversations.

    :user: User, who posted the message.
    :conversations: Conversation, which contains this message.
    :date: Date the message was posted.
    :text: Message text.

    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        related_name="messages",
        null=True,
        on_delete=models.SET_NULL,
    )

    conversation = models.ForeignKey(
        Conversation,
        verbose_name=_("Conversation"),
        related_name="messages",
        on_delete=models.CASCADE,
    )

    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date"),
    )

    last_edit = models.DateTimeField(auto_now=True, verbose_name=_("Last edit"), blank=True)

    text = models.TextField(
        max_length=4096,
        verbose_name=_("Text"),
    )

    attachment = models.FileField(
        upload_to="conversation_messages",
        verbose_name=_("Attachment"),
        blank=True,
        null=True,
        validators=[FileSizeValidator(10 * 1024 * 1024)],
    )

    class Meta:
        ordering = ("-date",)
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

    def __str__(self):
        return self.user.email

    def filename(self):
        if self.attachment:  # pragma: nocover
            return os.path.basename(self.attachment.name)
        return ""

    def get_absolute_url(self):
        return reverse("message-detail", args=[self.conversation.pk, self.pk])


# class BlockedUser(models.Model):
#     """
#     Model to mark a user relationship as blocked.

#     :user: Blocked user.
#     :blocked_by: User who blocked the other one.
#     :date: Date, the user has been blocked.

#     """

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         verbose_name=_("Blocked user"),
#         related_name="blocked",
#         on_delete=models.CASCADE,
#     )

#     blocked_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         verbose_name=_("Blocked by"),
#         related_name="blocked_users",
#         on_delete=models.CASCADE,
#     )

#     date = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Date"),
#     )

#     class Meta:
#         ordering = ("-date",)
#         verbose_name = _("Blocked user")
#         verbose_name_plural = _("Blocked users")

#     def __str__(self):
#         return self.user.email
