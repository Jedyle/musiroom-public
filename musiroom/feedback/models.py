from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator


class Feedback(models.Model):
    type = models.CharField(
        choices=settings.FEEDBACK_CHOICES, max_length=100, verbose_name=_("Type")
    )
    message = models.TextField(verbose_name=_("Message"), validators=[MinLengthValidator(10)])
    time = models.DateTimeField(auto_now_add=True, verbose_name=_("Time"))
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["-time"]

    def __str__(self):
        return self.message

    def get_absolute_url(self):
        return reverse("admin:view-feedback", args=[self.id])
