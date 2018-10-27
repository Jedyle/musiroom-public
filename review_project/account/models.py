import sys
from datetime import date
from io import BytesIO

from django.db import models
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver

from PIL import Image

from review_project.utils import make_clickable_link as _link

from django_comments_xtd.signals import confirmation_received
from lists.models import ItemList
from notifications.signals import notify
from pinax.badges.signals import badge_awarded
from actstream import action

from .badges import *


def get_100_last_years():
    lastyear = date.today().year
    return [str(i) for i in range(lastyear-1, lastyear-100, -1)]

def user_avatar_path(instance, filename):
    return 'avatars/user_{0}/{1}'.format(instance.user.id, filename)

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField("Avatar", null = True, blank = True, upload_to=user_avatar_path)
    birth = models.DateField("Date de naissance", null = True, blank = True)
    description = models.TextField("Description", max_length = 400, default = "", blank = True)

    SEX = [
        ("M","Homme"),
        ("F","Femme"),
        ("N","Anonyme"),
    ]

    sex = models.CharField("Sexe", max_length=1, default="N" , choices = SEX)
    display_birth = models.BooleanField("Afficher naissance", default = False)
    display_name = models.BooleanField("Afficher nom", default = False)
    display_sex = models.BooleanField("Afficher sexe", default = False)
    top_albums = models.ForeignKey(ItemList, blank=True, null=True, on_delete=models.PROTECT)

    last_activity = models.DateTimeField('Dernière activité', auto_now_add=True)

    def __str__(self):
        return self.user.username

    def get_age(self):
        born = self.birth
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        else:
            return static('account/images/profile.png')

    def get_absolute_url(self):
        return self.user.get_absolute_url()

    def save(self):
        if self.avatar:
            im = Image.open(self.avatar)
            output = BytesIO()
            im = im.convert('RGB')
            im.thumbnail((300,300))
            im.save(output, format='JPEG', quality=90)
            output.seek(0)
            self.avatar = InMemoryUploadedFile(output,'ImageField', "%s.jpg" %self.avatar.name.split('.')[0], 'image/jpeg', sys.getsizeof(output), None)
        super(Account,self).save()

def comment_activity_str(comment):
    obj = comment.content_object
    model = ContentType.objects.get_for_model(obj)
    return _link(comment.user) + " a commenté " + _link(obj) + ' (' + str(model) + ')'

@receiver(confirmation_received)
def comment_activity(comment, request, **kwargs):
    action.send(comment.user, verb="a commenté", action_object=comment.xtd_comment, to_str=comment_activity_str(comment))


@receiver(badge_awarded)
def notify_badge_awarded(badge_award, **kwargs):
    notify.send(badge_award.user, recipient=badge_award.user, verb="Vous avez reçu le badge", target = badge_award, to_str = "Vous avez reçu le badge " + badge_award.name + ".")
    action.send(badge_award.user, verb='a reçu le badge', action_object = badge_award, to_str="<a href='{}'>{}</a>".format(badge_award.user.get_absolute_url(), str(badge_award.user)) + ' a reçu le badge ' + badge_award.name)

